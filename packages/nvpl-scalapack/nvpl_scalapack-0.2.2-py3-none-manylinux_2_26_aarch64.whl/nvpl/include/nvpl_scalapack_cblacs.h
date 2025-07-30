// Copyright (c) 2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.

#ifndef NVPL_SCALAPACK_CBLACS_H
#define NVPL_SCALAPACK_CBLACS_H

#include "nvpl_scalapack_types.h"

#ifdef __cplusplus
extern "C" {
#endif

void Cblacs_pinfo(nvpl_int_t *mpi_rank, nvpl_int_t *mpi_size);
void Cblacs_exit(nvpl_int_t keep_mpi);

void Cblacs_gridinit(nvpl_int_t *icontxt, char *grid_layout, nvpl_int_t nprow, nvpl_int_t npcol);
void Cblacs_gridexit(nvpl_int_t icontxt);

void Cblacs_set(nvpl_int_t icontxt, nvpl_int_t what, nvpl_int_t *val);
void Cblacs_get(nvpl_int_t icontxt, nvpl_int_t what, nvpl_int_t *val);
void Cblacs_setup(nvpl_int_t *mpi_rank, nvpl_int_t *mpi_size);

void Cblacs_gridmap(nvpl_int_t *icontxt, nvpl_int_t *usermap, nvpl_int_t ldup, nvpl_int_t nprow0, nvpl_int_t npcol0);
void Cblacs_gridinfo(nvpl_int_t icontxt, nvpl_int_t *nprow, nvpl_int_t *npcol, nvpl_int_t *myrow, nvpl_int_t *mycol);

void Cblacs_barrier(nvpl_int_t icontxt, char *scope);

nvpl_int_t Cblacs_pnum(nvpl_int_t icontxt, nvpl_int_t prow, nvpl_int_t pcol);
void Cblacs_pcoord(nvpl_int_t icontxt, nvpl_int_t nodenum, nvpl_int_t *prow, nvpl_int_t *pcol);

void Cblacs_freebuff(nvpl_int_t icontxt, nvpl_int_t wait);
void Cblacs_abort(nvpl_int_t icontxt, nvpl_int_t ierr);

#ifdef __cplusplus
}
#endif

#endif /* NVPL_SCALAPACK_CBLACS_H */
