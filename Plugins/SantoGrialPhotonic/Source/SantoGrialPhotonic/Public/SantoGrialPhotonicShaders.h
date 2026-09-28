#pragma once

#include "GlobalShader.h"
#include "ShaderParameterStruct.h"

class FPhotonicEmitSignalsCS : public FGlobalShader
{
    DECLARE_GLOBAL_SHADER(FPhotonicEmitSignalsCS);
    SHADER_USE_PARAMETER_STRUCT(FPhotonicEmitSignalsCS, FGlobalShader);

    BEGIN_SHADER_PARAMETER_STRUCT(FParameters, )
        SHADER_PARAMETER(uint32, NumNeurons)
        SHADER_PARAMETER(uint32, NumEdges)
        SHADER_PARAMETER(float, DeltaSeconds)
        SHADER_PARAMETER(float, Attenuation)
        SHADER_PARAMETER_RDG_BUFFER_SRV(StructuredBuffer<float4>, NeuronBuffer)
        SHADER_PARAMETER_RDG_BUFFER_SRV(StructuredBuffer<float4>, EdgeBuffer)
        SHADER_PARAMETER_RDG_BUFFER_UAV(RWStructuredBuffer<float4>, SignalBuffer)
    END_SHADER_PARAMETER_STRUCT()

    static bool ShouldCompilePermutation(const FGlobalShaderPermutationParameters& Parameters)
    {
        return IsFeatureLevelSupported(Parameters.Platform, ERHIFeatureLevel::SM5);
    }
};

class FPhotonicAccumulateFieldsCS : public FGlobalShader
{
    DECLARE_GLOBAL_SHADER(FPhotonicAccumulateFieldsCS);
    SHADER_USE_PARAMETER_STRUCT(FPhotonicAccumulateFieldsCS, FGlobalShader);

    BEGIN_SHADER_PARAMETER_STRUCT(FParameters, )
        SHADER_PARAMETER(uint32, NumNeurons)
        SHADER_PARAMETER(uint32, NumEdges)
        SHADER_PARAMETER_RDG_BUFFER_SRV(StructuredBuffer<float4>, SignalBuffer)
        SHADER_PARAMETER_RDG_BUFFER_UAV(RWStructuredBuffer<float4>, AccumulationBuffer)
    END_SHADER_PARAMETER_STRUCT()

    static bool ShouldCompilePermutation(const FGlobalShaderPermutationParameters& Parameters)
    {
        return IsFeatureLevelSupported(Parameters.Platform, ERHIFeatureLevel::SM5);
    }
};

class FPhotonicUpdateNeuronsCS : public FGlobalShader
{
    DECLARE_GLOBAL_SHADER(FPhotonicUpdateNeuronsCS);
    SHADER_USE_PARAMETER_STRUCT(FPhotonicUpdateNeuronsCS, FGlobalShader);

    BEGIN_SHADER_PARAMETER_STRUCT(FParameters, )
        SHADER_PARAMETER(uint32, NumNeurons)
        SHADER_PARAMETER(float, DeltaSeconds)
        SHADER_PARAMETER(float, ActivationThreshold)
        SHADER_PARAMETER_RDG_BUFFER_SRV(StructuredBuffer<float4>, NeuronInput)
        SHADER_PARAMETER_RDG_BUFFER_SRV(StructuredBuffer<float4>, AccumulationBuffer)
        SHADER_PARAMETER_RDG_BUFFER_UAV(RWStructuredBuffer<float4>, NeuronOutput)
    END_SHADER_PARAMETER_STRUCT()

    static bool ShouldCompilePermutation(const FGlobalShaderPermutationParameters& Parameters)
    {
        return IsFeatureLevelSupported(Parameters.Platform, ERHIFeatureLevel::SM5);
    }
};
