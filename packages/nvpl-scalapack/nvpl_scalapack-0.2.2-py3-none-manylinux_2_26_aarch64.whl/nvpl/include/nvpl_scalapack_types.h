// Copyright (c) 2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.

#ifndef NVPL_SCALAPACK_TYPES_H
#define NVPL_SCALAPACK_TYPES_H

#ifdef NVPL_ILP64
#include <stdint.h>
typedef int64_t nvpl_int_t;
#else
typedef int nvpl_int_t;
#endif /* NVPL_ILP64 */

#ifndef nvpl_scomplex_t
typedef struct {
  float real;
  float imag;
} nvpl_scomplex_t;
#endif /* nvpl_scomplex_t */

#ifndef nvpl_dcomplex_t
typedef struct {
  double real;
  double imag;
} nvpl_dcomplex_t;
#endif /* nvpl_dcomplex_t */

#endif /* NVPL_SCALAPACK_TYPES_H */
