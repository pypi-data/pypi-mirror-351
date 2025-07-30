// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/kind/registry.h>
#include <pxr/tf/pyStaticTokens.h>

using namespace pxr;

void wrapTokens()
{
    TF_PY_WRAP_PUBLIC_TOKENS("Tokens", KindTokens,
                             KIND_TOKENS);
}
