using UnrealBuildTool;

public class SantoGrialPhotonic : ModuleRules
{
    public SantoGrialPhotonic(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "RenderCore"
        });

        PrivateDependencyModuleNames.AddRange(new string[]
        {
            "Projects",
            "RHI"
        });
    }
}
