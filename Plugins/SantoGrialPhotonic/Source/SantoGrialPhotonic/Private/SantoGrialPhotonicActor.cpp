#include "SantoGrialPhotonicActor.h"

#include "ComputeShaderUtils.h"
#include "RenderGraphBuilder.h"
#include "RenderGraphUtils.h"
#include "RHIGPUReadback.h"
#include "RenderingThread.h"
#include "SantoGrialPhotonicGpuLayout.h"
#include "SantoGrialPhotonicShaders.h"

ASantoGrialPhotonicActor::ASantoGrialPhotonicActor()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickGroup = TG_PostPhysics;
}

void ASantoGrialPhotonicActor::BeginPlay()
{
    Super::BeginPlay();

    InitializeDeterministicGraph();
    UE_LOG(LogTemp, Log, TEXT("Santo Grial: initialized %d neurons and %d directed optical edges"),
        NeuronCount, EdgesPerNeuron * NeuronCount);
}

void ASantoGrialPhotonicActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    ConsumeCompletedSnapshots();

    if (bRunSimulation && InitialNeuronBuffer.Num() > 0 && InitialEdgeBuffer.Num() > 0)
    {
        ++FrameCounter;
        EnqueueSimulationStep(DeltaSeconds * SimulationTimeScale);
    }
}

void ASantoGrialPhotonicActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    FlushRenderingCommands();
    if (PendingReadback != nullptr)
    {
        delete PendingReadback;
        PendingReadback = nullptr;
    }
    NeuronBuffer.SafeRelease();
    EdgeBuffer.SafeRelease();
    FSantoGrialGpuSnapshot DiscardedSnapshot;
    while (CompletedSnapshots.Dequeue(DiscardedSnapshot))
    {
    }
    Super::EndPlay(EndPlayReason);
}

void ASantoGrialPhotonicActor::ConsumeCompletedSnapshots()
{
    FSantoGrialGpuSnapshot Snapshot;
    while (CompletedSnapshots.Dequeue(Snapshot))
    {
        const uint32 Checksum = CalculateStateChecksum(Snapshot.State);
        int32 ActiveNeurons = 0;
        double TotalEnergy = 0.0;

        for (int32 NeuronIndex = 0; NeuronIndex < Snapshot.State.Num() / 3; ++NeuronIndex)
        {
            const FVector4f OpticalState = Snapshot.State[NeuronIndex * 3 + 1];
            ActiveNeurons += OpticalState.Z > 0.0001f ? 1 : 0;
            TotalEnergy += static_cast<double>(OpticalState.W);
        }

        UE_LOG(LogTemp, Log,
            TEXT("Santo Grial GPU readback: frame=%llu checksum=%08x active=%d total_energy=%.6f"),
            Snapshot.FrameNumber,
            Checksum,
            ActiveNeurons,
            TotalEnergy);
    }
}

uint32 ASantoGrialPhotonicActor::CalculateStateChecksum(const TArray<FVector4f>& State)
{
    uint32 Hash = 2166136261u;
    for (const FVector4f& Value : State)
    {
        const uint32 Components[4] =
        {
            FMath::AsUInt(Value.X),
            FMath::AsUInt(Value.Y),
            FMath::AsUInt(Value.Z),
            FMath::AsUInt(Value.W)
        };

        for (const uint32 Component : Components)
        {
            Hash ^= Component;
            Hash *= 16777619u;
        }
    }
    return Hash;
}

void ASantoGrialPhotonicActor::InitializeDeterministicGraph()
{
    NeuronCount = FMath::Max(1, NeuronCount);
    EdgesPerNeuron = FMath::Max(1, EdgesPerNeuron);

    InitialNeuronBuffer.SetNumZeroed(NeuronCount * SantoGrialPhotonicGpu::NeuronFloat4Stride);
    InitialEdgeBuffer.SetNumZeroed(NeuronCount * EdgesPerNeuron);

    const float Radius = 1000.0f;
    for (int32 NeuronIndex = 0; NeuronIndex < NeuronCount; ++NeuronIndex)
    {
        const float NormalizedIndex = static_cast<float>(NeuronIndex) / static_cast<float>(NeuronCount);
        const float Angle = NormalizedIndex * 24.0f * PI + static_cast<float>(DeterministicSeed) * 0.001f;
        const float LocalRadius = Radius * FMath::Sqrt(FMath::Max(NormalizedIndex, 0.001f));
        const FVector3f Position(
            LocalRadius * FMath::Cos(Angle),
            LocalRadius * FMath::Sin(Angle),
            80.0f * FMath::Sin(Angle * 0.37f));

        const FVector3f Color(
            0.35f + 0.65f * FMath::Abs(FMath::Sin(Angle)),
            0.25f + 0.75f * FMath::Abs(FMath::Sin(Angle + 2.094f)),
            0.25f + 0.75f * FMath::Abs(FMath::Sin(Angle + 4.188f)));

        InitialNeuronBuffer[NeuronIndex * 3 + 0] =
            SantoGrialPhotonicGpu::MakeNeuronPosition(Position, 0.05f);
        InitialNeuronBuffer[NeuronIndex * 3 + 1] =
            SantoGrialPhotonicGpu::MakeNeuronOpticalState(0.0f, 450.0f + 120.0f * Color.X, 0.0f, 1.0f);
        InitialNeuronBuffer[NeuronIndex * 3 + 2] =
            SantoGrialPhotonicGpu::MakeNeuronColor(Color);
    }

    for (int32 Source = 0; Source < NeuronCount; ++Source)
    {
        for (int32 Slot = 0; Slot < EdgesPerNeuron; ++Slot)
        {
            const int32 EdgeIndex = Source * EdgesPerNeuron + Slot;
            const int32 Offset = 1 + ((Source * 17 + Slot * 13 + DeterministicSeed) % FMath::Max(1, NeuronCount - 1));
            const int32 Target = NeuronCount > 1 ? (Source + Offset) % NeuronCount : Source;
            const float Weight = 0.65f / static_cast<float>(1 + Slot);
            const float Delay = 0.002f * static_cast<float>(1 + Slot);
            InitialEdgeBuffer[EdgeIndex] = SantoGrialPhotonicGpu::MakeEdge(Source, Target, Weight, Delay);
        }
    }
}

void ASantoGrialPhotonicActor::InjectPulse(
    int32 NeuronIndex,
    float Intensity,
    FLinearColor Color,
    float Frequency,
    float Phase)
{
    if (InitialNeuronBuffer.Num() == 0)
    {
        return;
    }

    const int32 ClampedIndex = FMath::Clamp(NeuronIndex, 0, NeuronCount - 1);
    InitialNeuronBuffer[ClampedIndex * 3 + 0].W = FMath::Max(0.0f, Intensity);
    InitialNeuronBuffer[ClampedIndex * 3 + 1] = FVector4f(Phase, Frequency, 1.0f, 1.0f);
    InitialNeuronBuffer[ClampedIndex * 3 + 2] = FVector4f(Color.R, Color.G, Color.B, 0.0f);

    if (bGpuInitialized)
    {
        UE_LOG(LogTemp, Warning, TEXT("Santo Grial: pulse injection after GPU start takes effect on restart; runtime upload is a later milestone."));
    }
}

void ASantoGrialPhotonicActor::EnqueueSimulationStep(float DeltaSeconds)
{
    const int32 LocalNeuronCount = NeuronCount;
    const int32 LocalEdgeCount = InitialEdgeBuffer.Num();
    const uint64 LocalFrameNumber = FrameCounter;
    const int32 LocalReadbackEveryNFrames = FMath::Max(1, ReadbackEveryNFrames);
    const float LocalAttenuation = FMath::Max(0.0f, OpticalAttenuation);
    const float LocalActivationThreshold = FMath::Max(0.0001f, ActivationThreshold);
    const TArray<FVector4f> LocalInitialNeurons = InitialNeuronBuffer;
    const TArray<FVector4f> LocalInitialEdges = InitialEdgeBuffer;

    ENQUEUE_RENDER_COMMAND(SantoGrialPhotonicSimulationStep)(
        [this, LocalNeuronCount, LocalEdgeCount, DeltaSeconds, LocalAttenuation,
         LocalActivationThreshold, LocalFrameNumber, LocalReadbackEveryNFrames,
         LocalInitialNeurons, LocalInitialEdges](FRHICommandListImmediate& RHICmdList)
        {
            FRDGBuilder GraphBuilder(RHICmdList);

            FRDGBufferRef NeuronInput = nullptr;
            if (NeuronBuffer.IsValid())
            {
                NeuronInput = GraphBuilder.RegisterExternalBuffer(NeuronBuffer, TEXT("SG_NeuronInput"));
            }
            else
            {
                const FRDGBufferDesc Desc = FRDGBufferDesc::CreateStructuredDesc(
                    sizeof(FVector4f), LocalNeuronCount * SantoGrialPhotonicGpu::NeuronFloat4Stride);
                NeuronInput = GraphBuilder.CreateBuffer(Desc, TEXT("SG_NeuronInput"));
                GraphBuilder.QueueBufferUpload(
                    NeuronInput,
                    LocalInitialNeurons.GetData(),
                    LocalInitialNeurons.Num() * sizeof(FVector4f));
            }

            FRDGBufferRef EdgeInput = nullptr;
            if (EdgeBuffer.IsValid())
            {
                EdgeInput = GraphBuilder.RegisterExternalBuffer(EdgeBuffer, TEXT("SG_EdgeInput"));
            }
            else
            {
                const FRDGBufferDesc Desc = FRDGBufferDesc::CreateStructuredDesc(
                    sizeof(FVector4f), LocalEdgeCount);
                EdgeInput = GraphBuilder.CreateBuffer(Desc, TEXT("SG_EdgeInput"));
                GraphBuilder.QueueBufferUpload(
                    EdgeInput,
                    LocalInitialEdges.GetData(),
                    LocalInitialEdges.Num() * sizeof(FVector4f));
            }

            const FRDGBufferDesc SignalDesc = FRDGBufferDesc::CreateStructuredDesc(
                sizeof(FVector4f), LocalEdgeCount * SantoGrialPhotonicGpu::SignalFloat4Stride);
            const FRDGBufferDesc AccumulationDesc = FRDGBufferDesc::CreateStructuredDesc(
                sizeof(FVector4f), LocalNeuronCount * SantoGrialPhotonicGpu::AccumulationFloat4Stride);
            const FRDGBufferDesc NeuronDesc = FRDGBufferDesc::CreateStructuredDesc(
                sizeof(FVector4f), LocalNeuronCount * SantoGrialPhotonicGpu::NeuronFloat4Stride);

            FRDGBufferRef SignalBuffer = GraphBuilder.CreateBuffer(SignalDesc, TEXT("SG_OpticalSignals"));
            FRDGBufferRef AccumulationBuffer = GraphBuilder.CreateBuffer(AccumulationDesc, TEXT("SG_CoherentFields"));
            FRDGBufferRef NeuronOutput = GraphBuilder.CreateBuffer(NeuronDesc, TEXT("SG_NeuronOutput"));

            {
                FPhotonicEmitSignalsCS::FParameters* Parameters =
                    GraphBuilder.AllocParameters<FPhotonicEmitSignalsCS::FParameters>();
                Parameters->NumNeurons = LocalNeuronCount;
                Parameters->NumEdges = LocalEdgeCount;
                Parameters->DeltaSeconds = DeltaSeconds;
                Parameters->Attenuation = LocalAttenuation;
                Parameters->NeuronBuffer = GraphBuilder.CreateSRV(NeuronInput);
                Parameters->EdgeBuffer = GraphBuilder.CreateSRV(EdgeInput);
                Parameters->SignalBuffer = GraphBuilder.CreateUAV(SignalBuffer);

                TShaderMapRef<FPhotonicEmitSignalsCS> Shader(GetGlobalShaderMap(GMaxRHIFeatureLevel));
                FComputeShaderUtils::AddPass(
                    GraphBuilder,
                    RDG_EVENT_NAME("SantoGrial.EmitSignals"),
                    Shader,
                    Parameters,
                    FIntVector(FMath::DivideAndRoundUp(LocalEdgeCount, 64), 1, 1));
            }

            {
                FPhotonicAccumulateFieldsCS::FParameters* Parameters =
                    GraphBuilder.AllocParameters<FPhotonicAccumulateFieldsCS::FParameters>();
                Parameters->NumNeurons = LocalNeuronCount;
                Parameters->NumEdges = LocalEdgeCount;
                Parameters->SignalBuffer = GraphBuilder.CreateSRV(SignalBuffer);
                Parameters->AccumulationBuffer = GraphBuilder.CreateUAV(AccumulationBuffer);

                TShaderMapRef<FPhotonicAccumulateFieldsCS> Shader(GetGlobalShaderMap(GMaxRHIFeatureLevel));
                FComputeShaderUtils::AddPass(
                    GraphBuilder,
                    RDG_EVENT_NAME("SantoGrial.AccumulateFields"),
                    Shader,
                    Parameters,
                    FIntVector(FMath::DivideAndRoundUp(LocalNeuronCount, 64), 1, 1));
            }

            {
                FPhotonicUpdateNeuronsCS::FParameters* Parameters =
                    GraphBuilder.AllocParameters<FPhotonicUpdateNeuronsCS::FParameters>();
                Parameters->NumNeurons = LocalNeuronCount;
                Parameters->DeltaSeconds = DeltaSeconds;
                Parameters->ActivationThreshold = LocalActivationThreshold;
                Parameters->NeuronInput = GraphBuilder.CreateSRV(NeuronInput);
                Parameters->AccumulationBuffer = GraphBuilder.CreateSRV(AccumulationBuffer);
                Parameters->NeuronOutput = GraphBuilder.CreateUAV(NeuronOutput);

                TShaderMapRef<FPhotonicUpdateNeuronsCS> Shader(GetGlobalShaderMap(GMaxRHIFeatureLevel));
                FComputeShaderUtils::AddPass(
                    GraphBuilder,
                    RDG_EVENT_NAME("SantoGrial.UpdateNeurons"),
                    Shader,
                    Parameters,
                    FIntVector(FMath::DivideAndRoundUp(LocalNeuronCount, 64), 1, 1));
            }

            const uint32 ReadbackBytes = LocalNeuronCount * SantoGrialPhotonicGpu::NeuronFloat4Stride * sizeof(FVector4f);
            if (PendingReadback != nullptr && PendingReadback->IsReady())
            {
                FSantoGrialGpuSnapshot Snapshot;
                Snapshot.FrameNumber = PendingReadbackFrameNumber;
                Snapshot.State.SetNumUninitialized(LocalNeuronCount * SantoGrialPhotonicGpu::NeuronFloat4Stride);

                const void* ReadbackData = PendingReadback->Lock(ReadbackBytes);
                FMemory::Memcpy(Snapshot.State.GetData(), ReadbackData, ReadbackBytes);
                PendingReadback->Unlock();
                delete PendingReadback;
                PendingReadback = nullptr;
                CompletedSnapshots.Enqueue(MoveTemp(Snapshot));
            }

            if (PendingReadback == nullptr && LocalFrameNumber % LocalReadbackEveryNFrames == 0)
            {
                PendingReadback = new FRHIGPUBufferReadback(TEXT("SantoGrialNeuronReadback"));
                PendingReadbackFrameNumber = LocalFrameNumber;
                AddEnqueueCopyPass(GraphBuilder, PendingReadback, NeuronOutput, ReadbackBytes);
            }

            GraphBuilder.QueueBufferExtraction(NeuronOutput, &NeuronBuffer);
            if (!EdgeBuffer.IsValid())
            {
                GraphBuilder.QueueBufferExtraction(EdgeInput, &EdgeBuffer);
            }

            GraphBuilder.Execute();
            bGpuInitialized = true;
        });
}
