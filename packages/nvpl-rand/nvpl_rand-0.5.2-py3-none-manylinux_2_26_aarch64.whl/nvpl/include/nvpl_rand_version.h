// Copyright (c) 2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.

#ifndef NVPL_RAND_VERSION_H
#define NVPL_RAND_VERSION_H

/// \def NVPL_RAND_VERSION
/// \brief NVPL RAND library version
///
/* \cond PRIVATE */
/// @note
/// NVPL_RAND_VERSION / 10000 - major version <br/>
/// NVPL_RAND_VERSION / 100 % 100 - minor version <br/>
/// NVPL_RAND_VERSION % 100 - patch level <br/>
/* \endcond */
#define NVPL_RAND_VERSION 502

#ifndef DOXYGEN_SHOULD_SKIP_THIS

#define NVPL_RAND_VERSION_MAJOR 0
#define NVPL_RAND_VERSION_MINOR 5
#define NVPL_RAND_VERSION_PATCH 2

#endif // DOXYGEN_SHOULD_SKIP_THIS

#endif // NVPL_RAND_VERSION_H
