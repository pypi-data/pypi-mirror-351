// Copyright (c) 2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.

#ifndef NVPL_SCALAPACK_PBLAS_H
#define NVPL_SCALAPACK_PBLAS_H

#include "nvpl_scalapack_types.h"

#ifdef __cplusplus
extern "C" {
#endif

///
/// level 1 functions
///

void psamax_(const nvpl_int_t *n, float *amax, nvpl_int_t *indx, const float *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx);
void pdamax_(const nvpl_int_t *n, double *amax, nvpl_int_t *indx, const double *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx);
void pcamax_(const nvpl_int_t *n, nvpl_scomplex_t *amax, nvpl_int_t *indx, const nvpl_scomplex_t *x,
             const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx);
void pzamax_(const nvpl_int_t *n, nvpl_dcomplex_t *amax, nvpl_int_t *indx, const nvpl_dcomplex_t *x,
             const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx);

void psasum_(const nvpl_int_t *n, float *asum, const float *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
             const nvpl_int_t *descx, const nvpl_int_t *incx);
void pdasum_(const nvpl_int_t *n, double *asum, const double *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
             const nvpl_int_t *descx, const nvpl_int_t *incx);

void pscasum_(const nvpl_int_t *n, float *asum, const nvpl_scomplex_t *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
              const nvpl_int_t *descx, const nvpl_int_t *incx);
void pdzasum_(const nvpl_int_t *n, double *asum, const nvpl_dcomplex_t *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
              const nvpl_int_t *descx, const nvpl_int_t *incx);

void psaxpy_(const nvpl_int_t *n, const float *a, const float *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
             const nvpl_int_t *descx, const nvpl_int_t *incx, float *y, const nvpl_int_t *iy, const nvpl_int_t *jy,
             const nvpl_int_t *descy, const nvpl_int_t *incy);
void pdaxpy_(const nvpl_int_t *n, const double *a, const double *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
             const nvpl_int_t *descx, const nvpl_int_t *incx, double *y, const nvpl_int_t *iy, const nvpl_int_t *jy,
             const nvpl_int_t *descy, const nvpl_int_t *incy);
void pcaxpy_(const nvpl_int_t *n, const nvpl_scomplex_t *a, const nvpl_scomplex_t *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, nvpl_scomplex_t *y,
             const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);
void pzaxpy_(const nvpl_int_t *n, const nvpl_dcomplex_t *a, const nvpl_dcomplex_t *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, nvpl_dcomplex_t *y,
             const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);

void picopy_(const nvpl_int_t *n, const nvpl_int_t *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
             const nvpl_int_t *descx, const nvpl_int_t *incx, nvpl_int_t *y, const nvpl_int_t *iy, const nvpl_int_t *jy,
             const nvpl_int_t *descy, const nvpl_int_t *incy);
void pscopy_(const nvpl_int_t *n, const float *x, const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx,
             const nvpl_int_t *incx, float *y, const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy,
             const nvpl_int_t *incy);
void pdcopy_(const nvpl_int_t *n, const double *x, const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx,
             const nvpl_int_t *incx, double *y, const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy,
             const nvpl_int_t *incy);
void pccopy_(const nvpl_int_t *n, const nvpl_scomplex_t *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
             const nvpl_int_t *descx, const nvpl_int_t *incx, nvpl_scomplex_t *y, const nvpl_int_t *iy,
             const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);
void pzcopy_(const nvpl_int_t *n, const nvpl_dcomplex_t *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
             const nvpl_int_t *descx, const nvpl_int_t *incx, nvpl_dcomplex_t *y, const nvpl_int_t *iy,
             const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);

void psdot_(const nvpl_int_t *n, float *dot, const float *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
            const nvpl_int_t *descx, const nvpl_int_t *incx, const float *y, const nvpl_int_t *iy, const nvpl_int_t *jy,
            const nvpl_int_t *descy, const nvpl_int_t *incy);
void pddot_(const nvpl_int_t *n, double *dot, const double *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
            const nvpl_int_t *descx, const nvpl_int_t *incx, const double *y, const nvpl_int_t *iy,
            const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);

void pcdotc_(const nvpl_int_t *n, nvpl_scomplex_t *dotc, const nvpl_scomplex_t *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, const nvpl_scomplex_t *y,
             const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);
void pzdotc_(const nvpl_int_t *n, nvpl_dcomplex_t *dotc, const nvpl_dcomplex_t *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, const nvpl_dcomplex_t *y,
             const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);

void pcdotu_(const nvpl_int_t *n, nvpl_scomplex_t *dotu, const nvpl_scomplex_t *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, const nvpl_scomplex_t *y,
             const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);
void pzdotu_(const nvpl_int_t *n, nvpl_dcomplex_t *dotu, const nvpl_dcomplex_t *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, const nvpl_dcomplex_t *y,
             const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);

void psnrm2_(const nvpl_int_t *n, float *norm2, const float *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
             const nvpl_int_t *descx, const nvpl_int_t *incx);
void pdnrm2_(const nvpl_int_t *n, double *norm2, const double *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
             const nvpl_int_t *descx, const nvpl_int_t *incx);
void pscnrm2_(const nvpl_int_t *n, float *norm2, const nvpl_scomplex_t *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
              const nvpl_int_t *descx, const nvpl_int_t *incx);
void pdznrm2_(const nvpl_int_t *n, double *norm2, const nvpl_dcomplex_t *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
              const nvpl_int_t *descx, const nvpl_int_t *incx);

void psscal_(const nvpl_int_t *n, const float *a, float *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
             const nvpl_int_t *descx, const nvpl_int_t *incx);
void pdscal_(const nvpl_int_t *n, const double *a, double *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
             const nvpl_int_t *descx, const nvpl_int_t *incx);
void pcscal_(const nvpl_int_t *n, const nvpl_scomplex_t *a, nvpl_scomplex_t *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx);
void pzscal_(const nvpl_int_t *n, const nvpl_dcomplex_t *a, nvpl_dcomplex_t *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx);
void pcsscal_(const nvpl_int_t *n, const float *a, nvpl_scomplex_t *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
              const nvpl_int_t *descx, const nvpl_int_t *incx);
void pzdscal_(const nvpl_int_t *n, const double *a, nvpl_dcomplex_t *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
              const nvpl_int_t *descx, const nvpl_int_t *incx);

void psswap_(const nvpl_int_t *n, float *x, const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx,
             const nvpl_int_t *incx, float *y, const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy,
             const nvpl_int_t *incy);
void pdswap_(const nvpl_int_t *n, double *x, const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx,
             const nvpl_int_t *incx, double *y, const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy,
             const nvpl_int_t *incy);
void pcswap_(const nvpl_int_t *n, nvpl_scomplex_t *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
             const nvpl_int_t *descx, const nvpl_int_t *incx, nvpl_scomplex_t *y, const nvpl_int_t *iy,
             const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);
void pzswap_(const nvpl_int_t *n, nvpl_dcomplex_t *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
             const nvpl_int_t *descx, const nvpl_int_t *incx, nvpl_dcomplex_t *y, const nvpl_int_t *iy,
             const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);

///
/// level 2 functions
///

void psgemv_(const char *trans, const nvpl_int_t *m, const nvpl_int_t *n, const float *alpha, const float *a,
             const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const float *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, const float *beta, float *y,
             const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);
void pdgemv_(const char *trans, const nvpl_int_t *m, const nvpl_int_t *n, const double *alpha, const double *a,
             const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const double *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, const double *beta, double *y,
             const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);
void pcgemv_(const char *trans, const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_scomplex_t *alpha,
             const nvpl_scomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca,
             const nvpl_scomplex_t *x, const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx,
             const nvpl_int_t *incx, const nvpl_scomplex_t *beta, nvpl_scomplex_t *y, const nvpl_int_t *iy,
             const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);
void pzgemv_(const char *trans, const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_dcomplex_t *alpha,
             const nvpl_dcomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca,
             const nvpl_dcomplex_t *x, const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx,
             const nvpl_int_t *incx, const nvpl_dcomplex_t *beta, nvpl_dcomplex_t *y, const nvpl_int_t *iy,
             const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);

void psagemv_(const char *trans, const nvpl_int_t *m, const nvpl_int_t *n, const float *alpha, const float *a,
              const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const float *x, const nvpl_int_t *ix,
              const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, const float *beta, float *y,
              const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);
void pdagemv_(const char *trans, const nvpl_int_t *m, const nvpl_int_t *n, const double *alpha, const double *a,
              const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const double *x,
              const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx,
              const double *beta, double *y, const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy,
              const nvpl_int_t *incy);
void pcagemv_(const char *trans, const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_scomplex_t *alpha,
              const nvpl_scomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca,
              const nvpl_scomplex_t *x, const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx,
              const nvpl_int_t *incx, const nvpl_scomplex_t *beta, nvpl_scomplex_t *y, const nvpl_int_t *iy,
              const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);
void pzagemv_(const char *trans, const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_dcomplex_t *alpha,
              const nvpl_dcomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca,
              const nvpl_dcomplex_t *x, const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx,
              const nvpl_int_t *incx, const nvpl_dcomplex_t *beta, nvpl_dcomplex_t *y, const nvpl_int_t *iy,
              const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);

void psger_(const nvpl_int_t *m, const nvpl_int_t *n, const float *alpha, const float *x, const nvpl_int_t *ix,
            const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, const float *y, const nvpl_int_t *iy,
            const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy, float *a, const nvpl_int_t *ia,
            const nvpl_int_t *ja, const nvpl_int_t *desca);
void pdger_(const nvpl_int_t *m, const nvpl_int_t *n, const double *alpha, const double *x, const nvpl_int_t *ix,
            const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, const double *y,
            const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy, double *a,
            const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca);

void pcgerc_(const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_scomplex_t *alpha, const nvpl_scomplex_t *x,
             const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx,
             const nvpl_scomplex_t *y, const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy,
             const nvpl_int_t *incy, nvpl_scomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
             const nvpl_int_t *desca);
void pzgerc_(const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_dcomplex_t *alpha, const nvpl_dcomplex_t *x,
             const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx,
             const nvpl_dcomplex_t *y, const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy,
             const nvpl_int_t *incy, nvpl_dcomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
             const nvpl_int_t *desca);

void pcgeru_(const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_scomplex_t *alpha, const nvpl_scomplex_t *x,
             const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx,
             const nvpl_scomplex_t *y, const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy,
             const nvpl_int_t *incy, nvpl_scomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
             const nvpl_int_t *desca);
void pzgeru_(const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_dcomplex_t *alpha, const nvpl_dcomplex_t *x,
             const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx,
             const nvpl_dcomplex_t *y, const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy,
             const nvpl_int_t *incy, nvpl_dcomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
             const nvpl_int_t *desca);

void pchemv_(const char *uplo, const nvpl_int_t *n, const nvpl_scomplex_t *alpha, const nvpl_scomplex_t *a,
             const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const nvpl_scomplex_t *x,
             const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx,
             const nvpl_scomplex_t *beta, nvpl_scomplex_t *y, const nvpl_int_t *iy, const nvpl_int_t *jy,
             const nvpl_int_t *descy, const nvpl_int_t *incy);
void pzhemv_(const char *uplo, const nvpl_int_t *n, const nvpl_dcomplex_t *alpha, const nvpl_dcomplex_t *a,
             const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const nvpl_dcomplex_t *x,
             const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx,
             const nvpl_dcomplex_t *beta, nvpl_dcomplex_t *y, const nvpl_int_t *iy, const nvpl_int_t *jy,
             const nvpl_int_t *descy, const nvpl_int_t *incy);
void pcahemv_(const char *uplo, const nvpl_int_t *n, const nvpl_scomplex_t *alpha, const nvpl_scomplex_t *a,
              const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const nvpl_scomplex_t *x,
              const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx,
              const nvpl_scomplex_t *beta, nvpl_scomplex_t *y, const nvpl_int_t *iy, const nvpl_int_t *jy,
              const nvpl_int_t *descy, const nvpl_int_t *incy);
void pzahemv_(const char *uplo, const nvpl_int_t *n, const nvpl_dcomplex_t *alpha, const nvpl_dcomplex_t *a,
              const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const nvpl_dcomplex_t *x,
              const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx,
              const nvpl_dcomplex_t *beta, nvpl_dcomplex_t *y, const nvpl_int_t *iy, const nvpl_int_t *jy,
              const nvpl_int_t *descy, const nvpl_int_t *incy);

void pcher_(const char *uplo, const nvpl_int_t *n, const float *alpha, const nvpl_scomplex_t *x, const nvpl_int_t *ix,
            const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, nvpl_scomplex_t *a,
            const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca);
void pzher_(const char *uplo, const nvpl_int_t *n, const double *alpha, const nvpl_dcomplex_t *x, const nvpl_int_t *ix,
            const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, nvpl_dcomplex_t *a,
            const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca);

void pcher2_(const char *uplo, const nvpl_int_t *n, const nvpl_scomplex_t *alpha, const nvpl_scomplex_t *x,
             const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx,
             const nvpl_scomplex_t *y, const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy,
             const nvpl_int_t *incy, nvpl_scomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
             const nvpl_int_t *desca);
void pzher2_(const char *uplo, const nvpl_int_t *n, const nvpl_dcomplex_t *alpha, const nvpl_dcomplex_t *x,
             const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx,
             const nvpl_dcomplex_t *y, const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy,
             const nvpl_int_t *incy, nvpl_dcomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
             const nvpl_int_t *desca);

void pssymv_(const char *uplo, const nvpl_int_t *n, const float *alpha, const float *a, const nvpl_int_t *ia,
             const nvpl_int_t *ja, const nvpl_int_t *desca, const float *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
             const nvpl_int_t *descx, const nvpl_int_t *incx, const float *beta, float *y, const nvpl_int_t *iy,
             const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);
void pdsymv_(const char *uplo, const nvpl_int_t *n, const double *alpha, const double *a, const nvpl_int_t *ia,
             const nvpl_int_t *ja, const nvpl_int_t *desca, const double *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
             const nvpl_int_t *descx, const nvpl_int_t *incx, const double *beta, double *y, const nvpl_int_t *iy,
             const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);

void psasymv_(const char *uplo, const nvpl_int_t *n, const float *alpha, const float *a, const nvpl_int_t *ia,
              const nvpl_int_t *ja, const nvpl_int_t *desca, const float *x, const nvpl_int_t *ix, const nvpl_int_t *jx,
              const nvpl_int_t *descx, const nvpl_int_t *incx, const float *beta, float *y, const nvpl_int_t *iy,
              const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);
void pdasymv_(const char *uplo, const nvpl_int_t *n, const double *alpha, const double *a, const nvpl_int_t *ia,
              const nvpl_int_t *ja, const nvpl_int_t *desca, const double *x, const nvpl_int_t *ix,
              const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, const double *beta, double *y,
              const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);

void pssyr_(const char *uplo, const nvpl_int_t *n, const float *alpha, const float *x, const nvpl_int_t *ix,
            const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, float *a, const nvpl_int_t *ia,
            const nvpl_int_t *ja, const nvpl_int_t *desca);
void pdsyr_(const char *uplo, const nvpl_int_t *n, const double *alpha, const double *x, const nvpl_int_t *ix,
            const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, double *a, const nvpl_int_t *ia,
            const nvpl_int_t *ja, const nvpl_int_t *desca);

void pssyr2_(const char *uplo, const nvpl_int_t *n, const float *alpha, const float *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, const float *y,
             const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy, float *a,
             const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca);
void pdsyr2_(const char *uplo, const nvpl_int_t *n, const double *alpha, const double *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx, const double *y,
             const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy, double *a,
             const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca);

void pstrmv_(const char *uplo, const char *trans, const char *diag, const nvpl_int_t *n, const float *a,
             const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, float *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx);
void pdtrmv_(const char *uplo, const char *trans, const char *diag, const nvpl_int_t *n, const double *a,
             const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, double *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx);
void pctrmv_(const char *uplo, const char *trans, const char *diag, const nvpl_int_t *n, const nvpl_scomplex_t *a,
             const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, nvpl_scomplex_t *x,
             const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx);
void pztrmv_(const char *uplo, const char *trans, const char *diag, const nvpl_int_t *n, const nvpl_dcomplex_t *a,
             const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, nvpl_dcomplex_t *x,
             const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx);

void psatrmv_(const char *uplo, const char *trans, const char *diag, const nvpl_int_t *n, const float *alpha,
              const float *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const float *x,
              const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx,
              const float *beta, float *y, const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy,
              const nvpl_int_t *incy);
void pdatrmv_(const char *uplo, const char *trans, const char *diag, const nvpl_int_t *n, const double *alpha,
              const double *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const double *x,
              const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx,
              const double *beta, double *y, const nvpl_int_t *iy, const nvpl_int_t *jy, const nvpl_int_t *descy,
              const nvpl_int_t *incy);
void pcatrmv_(const char *uplo, const char *trans, const char *diag, const nvpl_int_t *n, const nvpl_scomplex_t *alpha,
              const nvpl_scomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca,
              const nvpl_scomplex_t *x, const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx,
              const nvpl_int_t *incx, const nvpl_scomplex_t *beta, nvpl_scomplex_t *y, const nvpl_int_t *iy,
              const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);
void pzatrmv_(const char *uplo, const char *trans, const char *diag, const nvpl_int_t *n, const nvpl_dcomplex_t *alpha,
              const nvpl_dcomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca,
              const nvpl_dcomplex_t *x, const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx,
              const nvpl_int_t *incx, const nvpl_dcomplex_t *beta, nvpl_dcomplex_t *y, const nvpl_int_t *iy,
              const nvpl_int_t *jy, const nvpl_int_t *descy, const nvpl_int_t *incy);

void pstrsv_(const char *uplo, const char *trans, const char *diag, const nvpl_int_t *n, const float *a,
             const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, float *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx);
void pdtrsv_(const char *uplo, const char *trans, const char *diag, const nvpl_int_t *n, const double *a,
             const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, double *x, const nvpl_int_t *ix,
             const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx);
void pctrsv_(const char *uplo, const char *trans, const char *diag, const nvpl_int_t *n, const nvpl_scomplex_t *a,
             const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, nvpl_scomplex_t *x,
             const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx);
void pztrsv_(const char *uplo, const char *trans, const char *diag, const nvpl_int_t *n, const nvpl_dcomplex_t *a,
             const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, nvpl_dcomplex_t *x,
             const nvpl_int_t *ix, const nvpl_int_t *jx, const nvpl_int_t *descx, const nvpl_int_t *incx);

///
/// level 3 functions
///

void psgemm_(const char *transa, const char *transb, const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_int_t *k,
             const float *alpha, const float *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca,
             const float *b, const nvpl_int_t *ib, const nvpl_int_t *jb, const nvpl_int_t *descb, const float *beta,
             float *c, const nvpl_int_t *ic, const nvpl_int_t *jc, const nvpl_int_t *descc);
void pdgemm_(const char *transa, const char *transb, const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_int_t *k,
             const double *alpha, const double *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca,
             const double *b, const nvpl_int_t *ib, const nvpl_int_t *jb, const nvpl_int_t *descb, const double *beta,
             double *c, const nvpl_int_t *ic, const nvpl_int_t *jc, const nvpl_int_t *descc);
void pcgemm_(const char *transa, const char *transb, const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_int_t *k,
             const nvpl_scomplex_t *alpha, const nvpl_scomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
             const nvpl_int_t *desca, const nvpl_scomplex_t *b, const nvpl_int_t *ib, const nvpl_int_t *jb,
             const nvpl_int_t *descb, const nvpl_scomplex_t *beta, nvpl_scomplex_t *c, const nvpl_int_t *ic,
             const nvpl_int_t *jc, const nvpl_int_t *descc);
void pzgemm_(const char *transa, const char *transb, const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_int_t *k,
             const nvpl_dcomplex_t *alpha, const nvpl_dcomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
             const nvpl_int_t *desca, const nvpl_dcomplex_t *b, const nvpl_int_t *ib, const nvpl_int_t *jb,
             const nvpl_int_t *descb, const nvpl_dcomplex_t *beta, nvpl_dcomplex_t *c, const nvpl_int_t *ic,
             const nvpl_int_t *jc, const nvpl_int_t *descc);

void pchemm_(const char *side, const char *uplo, const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_scomplex_t *alpha,
             const nvpl_scomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca,
             const nvpl_scomplex_t *b, const nvpl_int_t *ib, const nvpl_int_t *jb, const nvpl_int_t *descb,
             const nvpl_scomplex_t *beta, nvpl_scomplex_t *c, const nvpl_int_t *ic, const nvpl_int_t *jc,
             const nvpl_int_t *descc);
void pzhemm_(const char *side, const char *uplo, const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_dcomplex_t *alpha,
             const nvpl_dcomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca,
             const nvpl_dcomplex_t *b, const nvpl_int_t *ib, const nvpl_int_t *jb, const nvpl_int_t *descb,
             const nvpl_dcomplex_t *beta, nvpl_dcomplex_t *c, const nvpl_int_t *ic, const nvpl_int_t *jc,
             const nvpl_int_t *descc);

void pcherk_(const char *uplo, const char *trans, const nvpl_int_t *n, const nvpl_int_t *k, const float *alpha,
             const nvpl_scomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca,
             const float *beta, nvpl_scomplex_t *c, const nvpl_int_t *ic, const nvpl_int_t *jc,
             const nvpl_int_t *descc);
void pzherk_(const char *uplo, const char *trans, const nvpl_int_t *n, const nvpl_int_t *k, const double *alpha,
             const nvpl_dcomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca,
             const double *beta, nvpl_dcomplex_t *c, const nvpl_int_t *ic, const nvpl_int_t *jc,
             const nvpl_int_t *descc);

void pcher2k_(const char *uplo, const char *trans, const nvpl_int_t *n, const nvpl_int_t *k,
              const nvpl_scomplex_t *alpha, const nvpl_scomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
              const nvpl_int_t *desca, const nvpl_scomplex_t *b, const nvpl_int_t *ib, const nvpl_int_t *jb,
              const nvpl_int_t *descb, const float *beta, nvpl_scomplex_t *c, const nvpl_int_t *ic,
              const nvpl_int_t *jc, const nvpl_int_t *descc);
void pzher2k_(const char *uplo, const char *trans, const nvpl_int_t *n, const nvpl_int_t *k,
              const nvpl_dcomplex_t *alpha, const nvpl_dcomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
              const nvpl_int_t *desca, const nvpl_dcomplex_t *b, const nvpl_int_t *ib, const nvpl_int_t *jb,
              const nvpl_int_t *descb, const double *beta, nvpl_dcomplex_t *c, const nvpl_int_t *ic,
              const nvpl_int_t *jc, const nvpl_int_t *descc);

void pssymm_(const char *side, const char *uplo, const nvpl_int_t *m, const nvpl_int_t *n, const float *alpha,
             const float *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const float *b,
             const nvpl_int_t *ib, const nvpl_int_t *jb, const nvpl_int_t *descb, const float *beta, float *c,
             const nvpl_int_t *ic, const nvpl_int_t *jc, const nvpl_int_t *descc);
void pdsymm_(const char *side, const char *uplo, const nvpl_int_t *m, const nvpl_int_t *n, const double *alpha,
             const double *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const double *b,
             const nvpl_int_t *ib, const nvpl_int_t *jb, const nvpl_int_t *descb, const double *beta, double *c,
             const nvpl_int_t *ic, const nvpl_int_t *jc, const nvpl_int_t *descc);
void pcsymm_(const char *side, const char *uplo, const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_scomplex_t *alpha,
             const nvpl_scomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca,
             const nvpl_scomplex_t *b, const nvpl_int_t *ib, const nvpl_int_t *jb, const nvpl_int_t *descb,
             const nvpl_scomplex_t *beta, nvpl_scomplex_t *c, const nvpl_int_t *ic, const nvpl_int_t *jc,
             const nvpl_int_t *descc);
void pzsymm_(const char *side, const char *uplo, const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_dcomplex_t *alpha,
             const nvpl_dcomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca,
             const nvpl_dcomplex_t *b, const nvpl_int_t *ib, const nvpl_int_t *jb, const nvpl_int_t *descb,
             const nvpl_dcomplex_t *beta, nvpl_dcomplex_t *c, const nvpl_int_t *ic, const nvpl_int_t *jc,
             const nvpl_int_t *descc);

void pssyrk_(const char *uplo, const char *trans, const nvpl_int_t *n, const nvpl_int_t *k, const float *alpha,
             const float *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const float *beta,
             float *c, const nvpl_int_t *ic, const nvpl_int_t *jc, const nvpl_int_t *descc);
void pdsyrk_(const char *uplo, const char *trans, const nvpl_int_t *n, const nvpl_int_t *k, const double *alpha,
             const double *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const double *beta,
             double *c, const nvpl_int_t *ic, const nvpl_int_t *jc, const nvpl_int_t *descc);
void pcsyrk_(const char *uplo, const char *trans, const nvpl_int_t *n, const nvpl_int_t *k,
             const nvpl_scomplex_t *alpha, const nvpl_scomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
             const nvpl_int_t *desca, const nvpl_scomplex_t *beta, nvpl_scomplex_t *c, const nvpl_int_t *ic,
             const nvpl_int_t *jc, const nvpl_int_t *descc);
void pzsyrk_(const char *uplo, const char *trans, const nvpl_int_t *n, const nvpl_int_t *k,
             const nvpl_dcomplex_t *alpha, const nvpl_dcomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
             const nvpl_int_t *desca, const nvpl_dcomplex_t *beta, nvpl_dcomplex_t *c, const nvpl_int_t *ic,
             const nvpl_int_t *jc, const nvpl_int_t *descc);

void pssyr2k_(const char *uplo, const char *trans, const nvpl_int_t *n, const nvpl_int_t *k, const float *alpha,
              const float *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const float *b,
              const nvpl_int_t *ib, const nvpl_int_t *jb, const nvpl_int_t *descb, const float *beta, float *c,
              const nvpl_int_t *ic, const nvpl_int_t *jc, const nvpl_int_t *descc);
void pdsyr2k_(const char *uplo, const char *trans, const nvpl_int_t *n, const nvpl_int_t *k, const double *alpha,
              const double *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const double *b,
              const nvpl_int_t *ib, const nvpl_int_t *jb, const nvpl_int_t *descb, const double *beta, double *c,
              const nvpl_int_t *ic, const nvpl_int_t *jc, const nvpl_int_t *descc);
void pcsyr2k_(const char *uplo, const char *trans, const nvpl_int_t *n, const nvpl_int_t *k,
              const nvpl_scomplex_t *alpha, const nvpl_scomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
              const nvpl_int_t *desca, const nvpl_scomplex_t *b, const nvpl_int_t *ib, const nvpl_int_t *jb,
              const nvpl_int_t *descb, const nvpl_scomplex_t *beta, nvpl_scomplex_t *c, const nvpl_int_t *ic,
              const nvpl_int_t *jc, const nvpl_int_t *descc);
void pzsyr2k_(const char *uplo, const char *trans, const nvpl_int_t *n, const nvpl_int_t *k,
              const nvpl_dcomplex_t *alpha, const nvpl_dcomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
              const nvpl_int_t *desca, const nvpl_dcomplex_t *b, const nvpl_int_t *ib, const nvpl_int_t *jb,
              const nvpl_int_t *descb, const nvpl_dcomplex_t *beta, nvpl_dcomplex_t *c, const nvpl_int_t *ic,
              const nvpl_int_t *jc, const nvpl_int_t *descc);

void pstran_(const nvpl_int_t *m, const nvpl_int_t *n, const float *alpha, const float *a, const nvpl_int_t *ia,
             const nvpl_int_t *ja, const nvpl_int_t *desca, const float *beta, float *c, const nvpl_int_t *ic,
             const nvpl_int_t *jc, const nvpl_int_t *descc);
void pdtran_(const nvpl_int_t *m, const nvpl_int_t *n, const double *alpha, const double *a, const nvpl_int_t *ia,
             const nvpl_int_t *ja, const nvpl_int_t *desca, const double *beta, double *c, const nvpl_int_t *ic,
             const nvpl_int_t *jc, const nvpl_int_t *descc);

void pctranu_(const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_scomplex_t *alpha, const nvpl_scomplex_t *a,
              const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const nvpl_scomplex_t *beta,
              nvpl_scomplex_t *c, const nvpl_int_t *ic, const nvpl_int_t *jc, const nvpl_int_t *descc);
void pztranu_(const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_dcomplex_t *alpha, const nvpl_dcomplex_t *a,
              const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const nvpl_dcomplex_t *beta,
              nvpl_dcomplex_t *c, const nvpl_int_t *ic, const nvpl_int_t *jc, const nvpl_int_t *descc);

void pctranc_(const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_scomplex_t *alpha, const nvpl_scomplex_t *a,
              const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const nvpl_scomplex_t *beta,
              nvpl_scomplex_t *c, const nvpl_int_t *ic, const nvpl_int_t *jc, const nvpl_int_t *descc);
void pztranc_(const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_dcomplex_t *alpha, const nvpl_dcomplex_t *a,
              const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const nvpl_dcomplex_t *beta,
              nvpl_dcomplex_t *c, const nvpl_int_t *ic, const nvpl_int_t *jc, const nvpl_int_t *descc);

void pstrmm_(const char *side, const char *uplo, const char *transa, const char *diag, const nvpl_int_t *m,
             const nvpl_int_t *n, const float *alpha, const float *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
             const nvpl_int_t *desca, float *b, const nvpl_int_t *ib, const nvpl_int_t *jb, const nvpl_int_t *descb);
void pdtrmm_(const char *side, const char *uplo, const char *transa, const char *diag, const nvpl_int_t *m,
             const nvpl_int_t *n, const double *alpha, const double *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
             const nvpl_int_t *desca, double *b, const nvpl_int_t *ib, const nvpl_int_t *jb, const nvpl_int_t *descb);
void pctrmm_(const char *side, const char *uplo, const char *transa, const char *diag, const nvpl_int_t *m,
             const nvpl_int_t *n, const nvpl_scomplex_t *alpha, const nvpl_scomplex_t *a, const nvpl_int_t *ia,
             const nvpl_int_t *ja, const nvpl_int_t *desca, nvpl_scomplex_t *b, const nvpl_int_t *ib,
             const nvpl_int_t *jb, const nvpl_int_t *descb);
void pztrmm_(const char *side, const char *uplo, const char *transa, const char *diag, const nvpl_int_t *m,
             const nvpl_int_t *n, const nvpl_dcomplex_t *alpha, const nvpl_dcomplex_t *a, const nvpl_int_t *ia,
             const nvpl_int_t *ja, const nvpl_int_t *desca, nvpl_dcomplex_t *b, const nvpl_int_t *ib,
             const nvpl_int_t *jb, const nvpl_int_t *descb);

void pstrsm_(const char *side, const char *uplo, const char *transa, const char *diag, const nvpl_int_t *m,
             const nvpl_int_t *n, const float *alpha, const float *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
             const nvpl_int_t *desca, float *b, const nvpl_int_t *ib, const nvpl_int_t *jb, const nvpl_int_t *descb);
void pdtrsm_(const char *side, const char *uplo, const char *transa, const char *diag, const nvpl_int_t *m,
             const nvpl_int_t *n, const double *alpha, const double *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
             const nvpl_int_t *desca, double *b, const nvpl_int_t *ib, const nvpl_int_t *jb, const nvpl_int_t *descb);
void pctrsm_(const char *side, const char *uplo, const char *transa, const char *diag, const nvpl_int_t *m,
             const nvpl_int_t *n, const nvpl_scomplex_t *alpha, const nvpl_scomplex_t *a, const nvpl_int_t *ia,
             const nvpl_int_t *ja, const nvpl_int_t *desca, nvpl_scomplex_t *b, const nvpl_int_t *ib,
             const nvpl_int_t *jb, const nvpl_int_t *descb);
void pztrsm_(const char *side, const char *uplo, const char *transa, const char *diag, const nvpl_int_t *m,
             const nvpl_int_t *n, const nvpl_dcomplex_t *alpha, const nvpl_dcomplex_t *a, const nvpl_int_t *ia,
             const nvpl_int_t *ja, const nvpl_int_t *desca, nvpl_dcomplex_t *b, const nvpl_int_t *ib,
             const nvpl_int_t *jb, const nvpl_int_t *descb);

void psgeadd_(const char *trans, const nvpl_int_t *m, const nvpl_int_t *n, const float *alpha, const float *a,
              const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const float *beta, float *c,
              const nvpl_int_t *ic, const nvpl_int_t *jc, const nvpl_int_t *descc);
void pdgeadd_(const char *trans, const nvpl_int_t *m, const nvpl_int_t *n, const double *alpha, const double *a,
              const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const double *beta, double *c,
              const nvpl_int_t *ic, const nvpl_int_t *jc, const nvpl_int_t *descc);
void pcgeadd_(const char *trans, const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_scomplex_t *alpha,
              const nvpl_scomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca,
              const nvpl_scomplex_t *beta, nvpl_scomplex_t *c, const nvpl_int_t *ic, const nvpl_int_t *jc,
              const nvpl_int_t *descc);
void pzgeadd_(const char *trans, const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_dcomplex_t *alpha,
              const nvpl_dcomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca,
              const nvpl_dcomplex_t *beta, nvpl_dcomplex_t *c, const nvpl_int_t *ic, const nvpl_int_t *jc,
              const nvpl_int_t *descc);

void pstradd_(const char *uplo, const char *trans, const nvpl_int_t *m, const nvpl_int_t *n, const float *alpha,
              const float *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const float *beta,
              float *c, const nvpl_int_t *ic, const nvpl_int_t *jc, const nvpl_int_t *descc);
void pdtradd_(const char *uplo, const char *trans, const nvpl_int_t *m, const nvpl_int_t *n, const double *alpha,
              const double *a, const nvpl_int_t *ia, const nvpl_int_t *ja, const nvpl_int_t *desca, const double *beta,
              double *c, const nvpl_int_t *ic, const nvpl_int_t *jc, const nvpl_int_t *descc);
void pctradd_(const char *uplo, const char *trans, const nvpl_int_t *m, const nvpl_int_t *n,
              const nvpl_scomplex_t *alpha, const nvpl_scomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
              const nvpl_int_t *desca, const nvpl_scomplex_t *beta, nvpl_scomplex_t *c, const nvpl_int_t *ic,
              const nvpl_int_t *jc, const nvpl_int_t *descc);
void pztradd_(const char *uplo, const char *trans, const nvpl_int_t *m, const nvpl_int_t *n,
              const nvpl_dcomplex_t *alpha, const nvpl_dcomplex_t *a, const nvpl_int_t *ia, const nvpl_int_t *ja,
              const nvpl_int_t *desca, const nvpl_dcomplex_t *beta, nvpl_dcomplex_t *c, const nvpl_int_t *ic,
              const nvpl_int_t *jc, const nvpl_int_t *descc);

nvpl_int_t pilaenv_(const nvpl_int_t *ictxt, const char *prec);

#ifdef __cplusplus
}
#endif

#endif /* NVPL_SCALAPACK_PBLAS_H */
