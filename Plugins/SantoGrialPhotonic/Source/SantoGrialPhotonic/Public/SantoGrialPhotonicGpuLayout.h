#pragma once

#include "CoreMinimal.h"

/**
 * GPU transport layout for the first vertical slice.
 *
 * Every record is a group of float4 values. This keeps the HLSL layout
 * explicit and avoids relying on FVector/FLinearColor packing rules.
 */
namespace SantoGrialPhotonicGpu
{
    static constexpr uint32 NeuronFloat4Stride = 3;
    static constexpr uint32 EdgeFloat4Stride = 1;
    static constexpr uint32 SignalFloat4Stride = 3;
    static constexpr uint32 AccumulationFloat4Stride = 2;

    FORCEINLINE FVector4f MakeNeuronPosition(const FVector3f& Position, float Intensity)
    {
        return FVector4f(Position.X, Position.Y, Position.Z, Intensity);
    }

    FORCEINLINE FVector4f MakeNeuronOpticalState(float Phase, float Frequency, float Activation, float Energy)
    {
        return FVector4f(Phase, Frequency, Activation, Energy);
    }

    FORCEINLINE FVector4f MakeNeuronColor(const FVector3f& Color)
    {
        return FVector4f(Color.X, Color.Y, Color.Z, 0.0f);
    }

    FORCEINLINE FVector4f MakeEdge(uint32 Source, uint32 Target, float Weight, float Delay)
    {
        return FVector4f(static_cast<float>(Source), static_cast<float>(Target), Weight, Delay);
    }
}
