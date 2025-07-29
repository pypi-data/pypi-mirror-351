// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "./debugCodes.h"
#include <pxr/tf/debug.h>
#include <pxr/tf/registryManager.h>

namespace pxr {

TF_REGISTRY_FUNCTION(pxr::TfDebug)
{
    TF_DEBUG_ENVIRONMENT_SYMBOL(PLUG_LOAD, "Plugin loading");
    TF_DEBUG_ENVIRONMENT_SYMBOL(PLUG_REGISTRATION, "Plugin registration");
    TF_DEBUG_ENVIRONMENT_SYMBOL(PLUG_LOAD_IN_SECONDARY_THREAD,
                                "Plugins loaded from non-main threads");
    TF_DEBUG_ENVIRONMENT_SYMBOL(PLUG_INFO_SEARCH, "Plugin info file search");
}

}  // namespace pxr
