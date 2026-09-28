#pragma once

#include "CoreMinimal.h"
#include "Containers/Queue.h"
#include "GameFramework/Actor.h"
#include "RenderGraphResources.h"
#include "SantoGrialPhotonicActor.generated.h"

class FRHIGPUBufferReadback;

struct FSantoGrialGpuSnapshot
{
    uint64 FrameNumber = 0;
    TArray<FVector4f> State;
};

/**
 * First vertical slice of Santo Grial:
 * fixed graph -> emitted optical-like signals -> coherent field accumulation
 * -> updated neuron state. The state is computed by GPU compute shaders.
 */
UCLASS(BlueprintType)
class SANTOGRIALPHOTONIC_API ASantoGrialPhotonicActor : public AActor
{
    GENERATED_BODY()

public:
    ASantoGrialPhotonicActor();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Santo Grial|Simulation", meta = (ClampMin = "1"))
    int32 NeuronCount = 1024;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Santo Grial|Simulation", meta = (ClampMin = "1"))
    int32 EdgesPerNeuron = 4;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Santo Grial|Simulation")
    int32 DeterministicSeed = 1337;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Santo Grial|Simulation")
    float SimulationTimeScale = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Santo Grial|Simulation", meta = (ClampMin = "0.0"))
    float OpticalAttenuation = 0.015f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Santo Grial|Simulation", meta = (ClampMin = "0.0001"))
    float ActivationThreshold = 0.25f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Santo Grial|Simulation")
    bool bRunSimulation = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Santo Grial|Validation", meta = (ClampMin = "1"))
    int32 ReadbackEveryNFrames = 30;

    UFUNCTION(BlueprintCallable, Category = "Santo Grial|Simulation")
    void InjectPulse(int32 NeuronIndex, float Intensity, FLinearColor Color, float Frequency, float Phase);

private:
    void InitializeDeterministicGraph();
    void EnqueueSimulationStep(float DeltaSeconds);

    TArray<FVector4f> InitialNeuronBuffer;
    TArray<FVector4f> InitialEdgeBuffer;

    TRefCountPtr<FRDGPooledBuffer> NeuronBuffer;
    TRefCountPtr<FRDGPooledBuffer> EdgeBuffer;
    FRHIGPUBufferReadback* PendingReadback = nullptr;
    uint64 PendingReadbackFrameNumber = 0;
    TQueue<FSantoGrialGpuSnapshot> CompletedSnapshots;
    uint64 FrameCounter = 0;
    bool bGpuInitialized = false;

    void ConsumeCompletedSnapshots();
    static uint32 CalculateStateChecksum(const TArray<FVector4f>& State);
};
