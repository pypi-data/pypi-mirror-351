#ifndef NVPL_LAPACK_SERVICE_H
#define NVPL_LAPACK_SERVICE_H

#include "nvpl_lapack_types.h"

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

/* Environment variable mode */

/* Returns current env mode */
nvpl_lapack_env_mode_t nvpl_lapack_get_env_mode();

/* Sets the global env mode of NVPL LAPACK. Default: NVPL_LAPACK_ENV_MODE_DEFAULT.
 *
 * Setting NVPL_LAPACK_ENV_MODE_USE_GLOBAL has no effect.
 */
void nvpl_lapack_set_env_mode(nvpl_lapack_env_mode_t env_mode);

/* Sets the thread local env mode of NVPL LAPACK. Default: use global env mode.
 * This function takes precedence over nvpl_lapack_set_env_mode().
 *
 * Setting NVPL_LAPACK_ENV_MODE_USE_GLOBAL will disable thread local env settings.
 *
 * Returns the previous value of local env mode. */
nvpl_lapack_env_mode_t nvpl_lapack_set_env_mode_local(
        nvpl_lapack_env_mode_t env_mode);

/* Math mode */

/* Returns current math mode */
nvpl_lapack_math_mode_t nvpl_lapack_get_math_mode();

/* Sets the global math mode of NVPL LAPACK. Default: NVPL_LAPACK_MATH_MODE_DEFAULT.
 *
 * Setting NVPL_LAPACK_MATH_MODE_USE_GLOBAL has no effect.
 */
void nvpl_lapack_set_math_mode(nvpl_lapack_math_mode_t math_mode);

/* Sets the thread local math mode of NVPL LAPACK. Default: use global math mode.
 * This function takes precedence over nvpl_lapack_set_math_mode().
 *
 * Setting NVPL_LAPACK_MATH_MODE_USE_GLOBAL will disable thread local math settings.
 *
 * Returns the previous value of local math mode. */
nvpl_lapack_math_mode_t nvpl_lapack_set_math_mode_local(
        nvpl_lapack_math_mode_t math_mode);

/* Threading control */

/* Returns the number of threads targeted for parallelism. */
int nvpl_lapack_get_max_threads();

/* Sets the global number of threads that NVPL LAPACK should use. Default: 0.
 * Use 0 to follow the threading runtime defaults. Negative nthr is ignored.
 * The function has no effect for sequential library. */
void nvpl_lapack_set_num_threads(int nthr);

/* Sets the local number of threads that NVPL LAPACK should use. Default: 0.
 * Use 0 to follow the global settings. Negative nthr_local is ignored.
 * This function takes precedence over nvpl_lapack_set_num_threads().
 * The function has no effect for sequential library.
 *
 * Returns the previous value of nthr_local. */
int nvpl_lapack_set_num_threads_local(int nthr_local);

/* Versioning */

/* Returns the library version as a single number.
 *
 * Returns (NVPL_LAPACK_VERSION_MAJOR * 10000 + NVPL_LAPACK_VERSION_MINOR * 100 + NVPL_LAPACK_VERSION_PATCH)
 */
int nvpl_lapack_get_version();

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif
