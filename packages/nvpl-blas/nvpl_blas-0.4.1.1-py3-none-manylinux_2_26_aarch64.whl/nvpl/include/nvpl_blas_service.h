#ifndef NVPL_BLAS_SERVICE_H
#define NVPL_BLAS_SERVICE_H

#include "nvpl_blas_types.h"

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

/* Version related */

/* Returns the library version as a single number.
 *
 * Returns (NVPL_BLAS_VERSION_MAJOR * 10000 +
 *          NVPL_BLAS_VERSION_MINOR * 100 +
 *          NVPL_BLAS_VERSION_PATCH)
 */
int NVPL_BLAS_API nvpl_blas_get_version();

/* Threading control */

/* Returns the number of threads targeted for parallelism. */
int NVPL_BLAS_API nvpl_blas_get_max_threads();

/* Sets the global number of threads that NVPL BLAS should use. Default: 0.
 * Use 0 to follow the threading runtime defaults. Negative nthr is ignored.
 * The function has no effect for sequential library. */
void NVPL_BLAS_API nvpl_blas_set_num_threads(int nthr);

/* Sets the local number of threads that NVPL BLAS should use. Default: 0.
 * Use 0 to follow the global settings. Negative nthr_local is ignored.
 * This function takes precedence over nvpl_blas_set_num_threads().
 * The function has no effect for sequential library.
 *
 * Returns the previous value of nthr_local. */
int NVPL_BLAS_API nvpl_blas_set_num_threads_local(int nthr_local);

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif
