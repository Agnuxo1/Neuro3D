#include "SantoGrialPhotonicShaders.h"

IMPLEMENT_GLOBAL_SHADER(
    FPhotonicEmitSignalsCS,
    "/Plugin/SantoGrialPhotonic/SantoGrialPhotonic.usf",
    "EmitSignalsCS",
    SF_Compute);

IMPLEMENT_GLOBAL_SHADER(
    FPhotonicAccumulateFieldsCS,
    "/Plugin/SantoGrialPhotonic/SantoGrialPhotonic.usf",
    "AccumulateFieldsCS",
    SF_Compute);

IMPLEMENT_GLOBAL_SHADER(
    FPhotonicUpdateNeuronsCS,
    "/Plugin/SantoGrialPhotonic/SantoGrialPhotonic.usf",
    "UpdateNeuronsCS",
    SF_Compute);
