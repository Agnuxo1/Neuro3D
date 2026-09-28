#include "CoreMinimal.h"
#include "Interfaces/IPluginManager.h"
#include "Misc/Paths.h"
#include "Modules/ModuleManager.h"
#include "ShaderCore.h"

class FSantoGrialPhotonicModule final : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        const TSharedPtr<IPlugin> Plugin = IPluginManager::Get().FindPlugin(TEXT("SantoGrialPhotonic"));
        if (Plugin.IsValid())
        {
            AddShaderSourceDirectoryMapping(
                TEXT("/Plugin/SantoGrialPhotonic"),
                FPaths::Combine(Plugin->GetBaseDir(), TEXT("Shaders")));
        }
    }
};

IMPLEMENT_MODULE(FSantoGrialPhotonicModule, SantoGrialPhotonic)
