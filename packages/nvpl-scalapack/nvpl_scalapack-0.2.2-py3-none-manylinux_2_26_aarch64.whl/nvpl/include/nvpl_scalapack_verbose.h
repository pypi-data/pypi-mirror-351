// Copyright (c) 2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.

#ifndef NVPL_SCALAPACK_VERBOSE_H
#define NVPL_SCALAPACK_VERBOSE_H

#ifdef __cplusplus
extern "C" {
#endif

///
/// verbose control
///
void nvpl_scalapack_set_verbose(const int flag);
void nvpl_scalapack_set_verbose_(const int *flag);

int nvpl_scalapack_get_verbose();
int nvpl_scalapack_get_verbose_();

#ifdef __cplusplus
}
#endif

#endif /* NVPL_SCALAPACK_BLACS_H */
