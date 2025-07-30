#if !defined(NVPL_SPARSE_H_)
#define NVPL_SPARSE_H_

#include <stdint.h>           // int64_t
#include <stdio.h>            // FILE*


#define NVPL_SPARSE_VER_MAJOR 0
#define NVPL_SPARSE_VER_MINOR 4
#define NVPL_SPARSE_VER_PATCH 1
#define NVPL_SPARSE_VER_BUILD 0
#define NVPL_SPARSE_VERSION (NVPL_SPARSE_VER_MAJOR * 1000 + \
                          NVPL_SPARSE_VER_MINOR *  100 + \
                          NVPL_SPARSE_VER_PATCH)


#if !defined(NVPL_SPARSE_API)
#    if defined(_WIN32)
#        define NVPL_SPARSE_API __stdcall
#    else
#        define NVPL_SPARSE_API
#    endif
#endif

#if !defined(_MSC_VER)
#   define NVPL_SPARSE_CPP_VERSION __cplusplus
#elif _MSC_FULL_VER >= 190024210 // Visual Studio 2015 Update 3
#   define NVPL_SPARSE_CPP_VERSION _MSVC_LANG
#else
#   define NVPL_SPARSE_CPP_VERSION 0
#endif


#if !defined(DISABLE_NVPL_SPARSE_DEPRECATED)

#   if NVPL_SPARSE_CPP_VERSION >= 201402L

#       define NVPL_SPARSE_DEPRECATED(new_func)                                   \
            [[deprecated("please use " #new_func " instead")]]

#   elif defined(_MSC_VER)

#       define NVPL_SPARSE_DEPRECATED(new_func)                                   \
            __declspec(deprecated("please use " #new_func " instead"))

#   elif defined(__INTEL_COMPILER) || defined(__clang__) ||                    \
         (defined(__GNUC__) &&                                                 \
          (__GNUC__ > 4 || (__GNUC__ == 4 && __GNUC_MINOR__ >= 5)))

#       define NVPL_SPARSE_DEPRECATED(new_func)                                   \
            __attribute__((deprecated("please use " #new_func " instead")))

#   elif defined(__GNUC__) || defined(__xlc__)

#       define NVPL_SPARSE_DEPRECATED(new_func)                                   \
            __attribute__((deprecated))

#   else

#       define NVPL_SPARSE_DEPRECATED(new_func)

#   endif // defined(__cplusplus) && __cplusplus >= 201402L
//------------------------------------------------------------------------------

#   if NVPL_SPARSE_CPP_VERSION >= 201703L

#       define NVPL_SPARSE_DEPRECATED_ENUM(new_enum)                              \
            [[deprecated("please use " #new_enum " instead")]]

#   elif defined(__clang__) ||                                                 \
         (defined(__GNUC__) && __GNUC__ >= 6 && !defined(__PGI))

#       define NVPL_SPARSE_DEPRECATED_ENUM(new_enum)                              \
            __attribute__((deprecated("please use " #new_enum " instead")))

#   else

#       define NVPL_SPARSE_DEPRECATED_ENUM(new_enum)

#   endif // defined(__cplusplus) && __cplusplus >= 201402L

#else // defined(DISABLE_NVPL_SPARSE_DEPRECATED)

#   define NVPL_SPARSE_DEPRECATED(new_func)
#   define NVPL_SPARSE_DEPRECATED_ENUM(new_enum)

#endif // !defined(DISABLE_NVPL_SPARSE_DEPRECATED)

#undef NVPL_SPARSE_CPP_VERSION


#if defined(__cplusplus)
extern "C" {
#endif // defined(__cplusplus)

struct nvpl_sparse_context;
typedef struct nvpl_sparse_context*       nvpl_sparse_handle_t;


//##############################################################################
//# Threading
//##############################################################################

int NVPL_SPARSE_API nvpl_sparse_get_max_threads(void);
int NVPL_SPARSE_API nvpl_sparse_get_num_threads(void);
void NVPL_SPARSE_API nvpl_sparse_set_num_threads(const int numthreads);
//int NVPL_SPARSE_API nvplsparse_get_num_procs(void);
int NVPL_SPARSE_API nvpl_sparse_get_thread_num(void);

//##############################################################################
//# ENUMERATORS
//##############################################################################

typedef enum {
    NVPL_SPARSE_STATUS_SUCCESS                   = 0,
    NVPL_SPARSE_STATUS_NOT_INITIALIZED           = 1,
    NVPL_SPARSE_STATUS_ALLOC_FAILED              = 2,
    NVPL_SPARSE_STATUS_INVALID_VALUE             = 3,
    NVPL_SPARSE_STATUS_ARCH_MISMATCH             = 4,
    NVPL_SPARSE_STATUS_MAPPING_ERROR             = 5,
    NVPL_SPARSE_STATUS_EXECUTION_FAILED          = 6,
    NVPL_SPARSE_STATUS_INTERNAL_ERROR            = 7,
    NVPL_SPARSE_STATUS_MATRIX_TYPE_NOT_SUPPORTED = 8,
    NVPL_SPARSE_STATUS_ZERO_PIVOT                = 9,
    NVPL_SPARSE_STATUS_NOT_SUPPORTED             = 10,
    NVPL_SPARSE_STATUS_INSUFFICIENT_RESOURCES    = 11
} nvpl_sparse_status_t;

typedef enum {
    NVPL_SPARSE_POINTER_MODE_HOST   = 0,
    NVPL_SPARSE_POINTER_MODE_DEVICE = 1
} nvpl_sparse_pointer_mode_t;

typedef enum {
    NVPL_SPARSE_ACTION_SYMBOLIC = 0,
    NVPL_SPARSE_ACTION_NUMERIC  = 1
} nvpl_sparse_action_t;

typedef enum {
    NVPL_SPARSE_FILL_MODE_LOWER = 0,
    NVPL_SPARSE_FILL_MODE_UPPER = 1
} nvpl_sparse_fill_mode_t;

typedef enum {
    NVPL_SPARSE_DIAG_TYPE_NON_UNIT = 0,
    NVPL_SPARSE_DIAG_TYPE_UNIT     = 1
} nvpl_sparse_diag_type_t;

typedef enum {
    NVPL_SPARSE_INDEX_BASE_ZERO = 0,
    NVPL_SPARSE_INDEX_BASE_ONE  = 1
} nvpl_sparse_index_base_t;

typedef enum {
    NVPL_SPARSE_OPERATION_NON_TRANSPOSE       = 0,
    NVPL_SPARSE_OPERATION_TRANSPOSE           = 1,
    NVPL_SPARSE_OPERATION_CONJUGATE_TRANSPOSE = 2
} nvpl_sparse_operation_t;

 typedef enum{
        NVPL_SPARSE_R_16F,
        NVPL_SPARSE_C_16F,
        NVPL_SPARSE_R_16BF,
        NVPL_SPARSE_C_16BF,
        NVPL_SPARSE_R_16I,
        NVPL_SPARSE_R_16U,
        NVPL_SPARSE_R_32F,
        NVPL_SPARSE_C_32F,
        NVPL_SPARSE_R_64F,
        NVPL_SPARSE_C_64F,
        NVPL_SPARSE_R_64I,
        NVPL_SPARSE_R_64U,
        NVPL_SPARSE_R_8I,
        NVPL_SPARSE_R_8U,
        NVPL_SPARSE_R_32I,
        NVPL_SPARSE_R_32U,
} nvpl_sparse_data_type_t;

//------------------------------------------------------------------------------


//##############################################################################
//# INITIALIZATION AND MANAGEMENT ROUTINES
//##############################################################################

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_create(nvpl_sparse_handle_t* handle);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_destroy(nvpl_sparse_handle_t handle);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_get_version(nvpl_sparse_handle_t handle,
                        int*             version);

// #############################################################################
// # GENERIC APIs - Enumerators and Opaque Data Structures
// #############################################################################

typedef enum {
    NVPL_SPARSE_FORMAT_CSR             = 1, ///< Compressed Sparse Row (CSR)
    NVPL_SPARSE_FORMAT_CSC             = 2, ///< Compressed Sparse Column (CSC)
    NVPL_SPARSE_FORMAT_COO             = 3, ///< Coordinate (COO) - Structure of Arrays
    NVPL_SPARSE_FORMAT_BLOCKED_ELL     = 5, ///< Blocked ELL
    NVPL_SPARSE_FORMAT_BSR             = 6, ///< Blocked Compressed Sparse Row (BSR)
    NVPL_SPARSE_FORMAT_SLICED_ELLPACK  = 7 ///< Sliced ELL
} nvpl_sparse_format_t;

typedef enum {
    NVPL_SPARSE_ORDER_COL = 1, ///< Column-Major Order - Matrix memory layout
    NVPL_SPARSE_ORDER_ROW = 2  ///< Row-Major Order - Matrix memory layout
} nvpl_sparse_order_t;

typedef enum {
    NVPL_SPARSE_INDEX_16U = 1, ///< 16-bit unsigned integer for matrix/vector
                            ///< indices
    NVPL_SPARSE_INDEX_32I = 2, ///< 32-bit signed integer for matrix/vector indices
    NVPL_SPARSE_INDEX_64I = 3  ///< 64-bit signed integer for matrix/vector indices
} nvpl_sparse_index_type_t;

//------------------------------------------------------------------------------

struct nvpl_sparse_sp_vec_descr;
struct nvpl_sparse_dn_vec_descr;
struct nvpl_sparse_sp_mat_descr;
struct nvpl_sparse_dn_mat_descr;

typedef struct nvpl_sparse_sp_vec_descr* nvpl_sparse_sp_vec_descr_t;
typedef struct nvpl_sparse_dn_vec_descr* nvpl_sparse_dn_vec_descr_t;
typedef struct nvpl_sparse_sp_mat_descr* nvpl_sparse_sp_mat_descr_t;
typedef struct nvpl_sparse_dn_mat_descr* nvpl_sparse_dn_mat_descr_t;

typedef struct nvpl_sparse_sp_vec_descr const* nvpl_sparse_const_sp_vec_descr_t;
typedef struct nvpl_sparse_dn_vec_descr const* nvpl_sparse_const_dn_vec_descr_t;
typedef struct nvpl_sparse_sp_mat_descr const* nvpl_sparse_const_sp_mat_descr_t;
typedef struct nvpl_sparse_dn_mat_descr const* nvpl_sparse_const_dn_mat_descr_t;


// // #############################################################################
// // # DENSE VECTOR DESCRIPTOR
// // #############################################################################

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_create_dn_vec(nvpl_sparse_dn_vec_descr_t*                   dn_vec_descr,
                    int64_t                                             size,
                    void*                                               values,
                    nvpl_sparse_data_type_t                             value_type);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_create_const_dn_vec(nvpl_sparse_const_dn_vec_descr_t*       dn_vec_descr,
                         int64_t                                        size,
                         const void*                                    values,
                         nvpl_sparse_data_type_t                        value_type);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_destroy_dn_vec(nvpl_sparse_const_dn_vec_descr_t         dn_vec_descr);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_dn_vec_get(nvpl_sparse_dn_vec_descr_t                   dn_vec_descr,
                int64_t*                                            size,
                void**                                              values,
                nvpl_sparse_data_type_t*                            value_type);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_const_dn_vec_get(nvpl_sparse_const_dn_vec_descr_t       dn_vec_descr,
                int64_t*                                            size,
                const void**                                        values,
                nvpl_sparse_data_type_t*                            value_type);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_dn_vec_get_values(nvpl_sparse_dn_vec_descr_t            dn_vec_descr,
                void**                                              values);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_const_dn_vec_get_values(nvpl_sparse_const_dn_vec_descr_t    dn_vec_descr,
                const void**                                            values);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_dn_vec_set_values(nvpl_sparse_dn_vec_descr_t            dn_vec_descr,
                void*                                               values);

// // #############################################################################
// // # SPARSE MATRIX DESCRIPTOR
// // #############################################################################

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_destroy_sp_mat(nvpl_sparse_const_sp_mat_descr_t             sp_mat_descr);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_sp_mat_get_format(nvpl_sparse_const_sp_mat_descr_t          sp_mat_descr,
                       nvpl_sparse_format_t*                            format);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_sp_mat_get_index_base(nvpl_sparse_const_sp_mat_descr_t      sp_mat_descr,
                          nvpl_sparse_index_base_t*                     idx_base);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_sp_mat_get_values(nvpl_sparse_sp_mat_descr_t                sp_mat_descr,
                       void**                                           values);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_const_sp_mat_get_values(nvpl_sparse_const_sp_mat_descr_t    sp_mat_descr,
                       const void**                                     values);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_sp_mat_set_values(nvpl_sparse_sp_mat_descr_t                sp_mat_descr,
                       void*                                            values);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_sp_mat_get_size(nvpl_sparse_const_sp_mat_descr_t            sp_mat_descr,
                     int64_t*                                           rows,
                     int64_t*                                           cols,
                     int64_t*                                           nnz);

typedef enum {
    NVPL_SPARSE_SPMAT_FILL_MODE,
    NVPL_SPARSE_SPMAT_DIAG_TYPE //, Add more please
} nvpl_sparse_sp_mat_attribute_t;

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_sp_mat_get_attribute(nvpl_sparse_const_sp_mat_descr_t   sp_mat_descr,
                          nvpl_sparse_sp_mat_attribute_t            attribute,
                          void*                                     data,
                          size_t                                    data_size);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_sp_mat_set_attribute(nvpl_sparse_sp_mat_descr_t         sp_mat_descr,
                          nvpl_sparse_sp_mat_attribute_t            attribute,
                          void*                                     data,
                          size_t                                    data_size);

//------------------------------------------------------------------------------
// ### CSR ###

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_create_csr(nvpl_sparse_sp_mat_descr_t*      sp_mat_descr,
                  int64_t                               rows,
                  int64_t                               cols,
                  int64_t                               nnz,
                  void*                                 csr_row_offsets,
                  void*                                 csr_col_ind,
                  void*                                 csr_values,
                  nvpl_sparse_index_type_t              csr_row_offsets_type,
                  nvpl_sparse_index_type_t              csr_col_ind_type,
                  nvpl_sparse_index_base_t              idx_base,
                  nvpl_sparse_data_type_t               value_type);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_create_const_csr(nvpl_sparse_const_sp_mat_descr_t*  sp_mat_descr,
                       int64_t                                  rows,
                       int64_t                                  cols,
                       int64_t                                  nnz,
                       const void*                              csr_row_offsets,
                       const void*                              csr_col_ind,
                       const void*                              csr_values,
                       nvpl_sparse_index_type_t                 csr_row_offsets_type,
                       nvpl_sparse_index_type_t                 csr_col_ind_type,
                       nvpl_sparse_index_base_t                 idx_base,
                       nvpl_sparse_data_type_t                  value_type);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_create_csc(nvpl_sparse_sp_mat_descr_t*  sp_mat_descr,
                  int64_t                           rows,
                  int64_t                           cols,
                  int64_t                           nnz,
                  void*                             csc_col_offsets,
                  void*                             csc_row_ind,
                  void*                             csc_values,
                  nvpl_sparse_index_type_t          cscColOffsetsType,
                  nvpl_sparse_index_type_t          csc_row_indType,
                  nvpl_sparse_index_base_t          idx_base,
                  nvpl_sparse_data_type_t           value_type);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_create_const_csc(nvpl_sparse_const_sp_mat_descr_t*  sp_mat_descr,
                       int64_t                                  rows,
                       int64_t                                  cols,
                       int64_t                                  nnz,
                       const void*                              csc_col_offsets,
                       const void*                              csc_row_ind,
                       const void*                              csc_values,
                       nvpl_sparse_index_type_t                 cscColOffsetsType,
                       nvpl_sparse_index_type_t                 csc_row_ind_type,
                       nvpl_sparse_index_base_t                 idx_base,
                       nvpl_sparse_data_type_t                  value_type);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_csr_get(nvpl_sparse_sp_mat_descr_t  sp_mat_descr,
               int64_t*                      rows,
               int64_t*                      cols,
               int64_t*                      nnz,
               void**                        csr_row_offsets,
               void**                        csr_col_ind,
               void**                        csr_values,
               nvpl_sparse_index_type_t*     csr_row_offsets_type,
               nvpl_sparse_index_type_t*     csr_col_ind_type,
               nvpl_sparse_index_base_t*     idx_base,
               nvpl_sparse_data_type_t*      value_type);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_const_csr_get(nvpl_sparse_const_sp_mat_descr_t    sp_mat_descr,
               int64_t*                                 rows,
               int64_t*                                 cols,
               int64_t*                                 nnz,
               const void**                             csr_row_offsets,
               const void**                             csr_col_ind,
               const void**                             csr_values,
               nvpl_sparse_index_type_t*                csr_row_offsets_type,
               nvpl_sparse_index_type_t*                csr_col_ind_type,
               nvpl_sparse_index_base_t*                idx_base,
               nvpl_sparse_data_type_t*                 value_type);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_csc_get(nvpl_sparse_sp_mat_descr_t   sp_mat_descr,
               int64_t*                          rows,
               int64_t*                          cols,
               int64_t*                          nnz,
               void**                            csc_col_offsets,
               void**                            csc_row_ind,
               void**                            csc_values,
               nvpl_sparse_index_type_t*         csc_col_offsets_type,
               nvpl_sparse_index_type_t*         csc_row_ind_type,
               nvpl_sparse_index_base_t*         idx_base,
               nvpl_sparse_data_type_t*          value_type);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_const_csc_get(nvpl_sparse_const_sp_mat_descr_t   sp_mat_descr,
               int64_t*                          rows,
               int64_t*                          cols,
               int64_t*                          nnz,
               const void**                      csc_col_offsets,
               const void**                      csc_row_ind,
               const void**                      csc_values,
               nvpl_sparse_index_type_t*         csc_col_offsets_type,
               nvpl_sparse_index_type_t*         csc_row_ind_type,
               nvpl_sparse_index_base_t*         idx_base,
               nvpl_sparse_data_type_t*          value_type);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_csr_set_pointers(nvpl_sparse_sp_mat_descr_t  sp_mat_descr,
                       void*                             csr_row_offsets,
                       void*                             csr_col_ind,
                       void*                             csr_values);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_csc_set_pointers(nvpl_sparse_sp_mat_descr_t  sp_mat_descr,
                       void*                             csc_col_offsets,
                       void*                             csc_row_ind,
                       void*                             csc_values);

//------------------------------------------------------------------------------
// ### COO ###

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_create_coo(nvpl_sparse_sp_mat_descr_t*  sp_mat_descr,
                  int64_t                           rows,
                  int64_t                           cols,
                  int64_t                           nnz,
                  void*                             coo_row_ind,
                  void*                             coo_col_ind,
                  void*                             coo_values,
                  nvpl_sparse_index_type_t          idx_type,
                  nvpl_sparse_index_base_t          idx_base,
                  nvpl_sparse_data_type_t           value_type);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_create_const_coo(nvpl_sparse_const_sp_mat_descr_t*  sp_mat_descr,
                  int64_t                                       rows,
                  int64_t                                       cols,
                  int64_t                                       nnz,
                  const void*                                   coo_row_ind,
                  const void*                                   coo_col_ind,
                  const void*                                   coo_values,
                  nvpl_sparse_index_type_t                      idx_type,
                  nvpl_sparse_index_base_t                      idx_base,
                  nvpl_sparse_data_type_t                       value_type);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_coo_get(nvpl_sparse_sp_mat_descr_t                   sp_mat_descr,
                  int64_t*                                       rows,
                  int64_t*                                       cols,
                  int64_t*                                       nnz,
                  void**                                         coo_row_ind,
                  void**                                         coo_col_ind,
                  void**                                         coo_values,
                  nvpl_sparse_index_type_t*                      idx_type,
                  nvpl_sparse_index_base_t*                      idx_base,
                  nvpl_sparse_data_type_t*                       value_type);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_const_coo_get(nvpl_sparse_const_sp_mat_descr_t       sp_mat_descr,
                  int64_t*                                       rows,
                  int64_t*                                       cols,
                  int64_t*                                       nnz,
                  const void**                                   coo_row_ind,
                  const void**                                   coo_col_ind,
                  const void**                                   coo_values,
                  nvpl_sparse_index_type_t*                      idx_type,
                  nvpl_sparse_index_base_t*                      idx_base,
                  nvpl_sparse_data_type_t*                       value_type);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_coo_set_pointers(nvpl_sparse_sp_mat_descr_t          sp_mat_descr,
                  void*                                          coo_row_ind,
                  void*                                          coo_col_ind,
                  void*                                          coo_values);

//------------------------------------------------------------------------------
// ### Sliced ELLPACK ###

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_create_sliced_ell(nvpl_sparse_sp_mat_descr_t*   sp_mat_descr,
                    int64_t                                 rows,
                    int64_t                                 cols,
                    int64_t                                 nnz,
                    int64_t                                 sell_values_size,
                    int64_t                                 slice_size,
                    void*                                   sell_slice_offsets,
                    void*                                   sell_col_ind,
                    void*                                   sell_values,
                    nvpl_sparse_index_type_t                sell_slice_offsets_type,
                    nvpl_sparse_index_type_t                sell_col_ind_type,
                    nvpl_sparse_index_base_t                idx_base,
                    nvpl_sparse_data_type_t                 value_type);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_create_const_sliced_ell(
                    nvpl_sparse_const_sp_mat_descr_t*   sp_mat_descr,
                    int64_t                             rows,
                    int64_t                             cols,
                    int64_t                             nnz,
                    int64_t                             sell_values_size,
                    int64_t                             slice_size,
                    const void*                         sell_slice_offsets,
                    const void*                         sell_col_ind,
                    const void*                         sell_values,
                    nvpl_sparse_index_type_t            sell_slice_offsets_type,
                    nvpl_sparse_index_type_t            sell_col_ind_type,
                    nvpl_sparse_index_base_t            idx_base,
                    nvpl_sparse_data_type_t             value_type);


// #############################################################################
// # SPARSE MATRIX-VECTOR MULTIPLICATION
// #############################################################################

struct nvpl_sparse_spmv_descr;
typedef struct nvpl_sparse_spmv_descr* nvpl_sparse_spmv_descr_t;

typedef enum {
    NVPL_SPARSE_SPMV_ALG_DEFAULT = 0,
    NVPL_SPARSE_SPMV_CSR_ALG1    = 2,
    NVPL_SPARSE_SPMV_CSR_ALG2    = 3,
    NVPL_SPARSE_SPMV_COO_ALG1    = 1,
    NVPL_SPARSE_SPMV_COO_ALG2    = 4,
    NVPL_SPARSE_SPMV_SELL_ALG1   = 5
} nvpl_sparse_spmv_alg_t;

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_spmv_create_descr(nvpl_sparse_spmv_descr_t* descr);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_spmv_destroy_descr(nvpl_sparse_spmv_descr_t descr);


nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_spmv(nvpl_sparse_handle_t           handle,
             nvpl_sparse_operation_t            op_A,
             const void*                        alpha,
             nvpl_sparse_const_sp_mat_descr_t   mat_A,
             nvpl_sparse_const_dn_vec_descr_t   vec_X,
             const void*                        beta,
             nvpl_sparse_dn_vec_descr_t         vec_Y,
             nvpl_sparse_dn_vec_descr_t         vec_Z,
             nvpl_sparse_data_type_t            compute_type,
             nvpl_sparse_spmv_alg_t             alg,
             nvpl_sparse_spmv_descr_t           spmv_descr);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_spmv_buffer_size(nvpl_sparse_handle_t           handle,
                        nvpl_sparse_operation_t             op_A,
                        const void*                         alpha,
                        nvpl_sparse_const_sp_mat_descr_t    mat_A,
                        nvpl_sparse_const_dn_vec_descr_t    vec_X,
                        const void*                         beta,
                        nvpl_sparse_dn_vec_descr_t          vec_Y,
                        nvpl_sparse_dn_vec_descr_t          vec_Z,
                        nvpl_sparse_data_type_t             compute_type,
                        nvpl_sparse_spmv_alg_t              alg,
                        nvpl_sparse_spmv_descr_t            spmv_descr,
                        size_t*                             buffer_size);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_spmv_analysis(nvpl_sparse_handle_t              handle,
                        nvpl_sparse_operation_t             op_A,
                        const void*                         alpha,
                        nvpl_sparse_const_sp_mat_descr_t    mat_A,
                        nvpl_sparse_const_dn_vec_descr_t    vec_X,
                        const void*                         beta,
                        nvpl_sparse_dn_vec_descr_t          vec_Y,
                        nvpl_sparse_dn_vec_descr_t          vec_Z,
                        nvpl_sparse_data_type_t             compute_type,
                        nvpl_sparse_spmv_alg_t              alg,
                        nvpl_sparse_spmv_descr_t            spmv_descr,
                        void*                               external_buffer);


// #############################################################################
// # SPARSE TRIANGULAR VECTOR SOLVE
// #############################################################################

typedef enum {
    NVPL_SPARSE_SPSV_ALG_DEFAULT = 0,
} nvpl_sparse_spsv_alg_t;

typedef enum {
    NVPL_SPARSE_SPSV_UPDATE_GENERAL  = 0,
    NVPL_SPARSE_SPSV_UPDATE_DIAGONAL = 1
} nvpl_sparse_spsv_update_t;

struct nvpl_sparse_spsv_descr;
typedef struct nvpl_sparse_spsv_descr* nvpl_sparse_spsv_descr_t;

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_spsv_create_descr(nvpl_sparse_spsv_descr_t* descr);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_spsv_destroy_descr(nvpl_sparse_spsv_descr_t descr);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_spsv_buffer_size(nvpl_sparse_handle_t           handle,
                        nvpl_sparse_operation_t             op_A,
                        const void*                         alpha,
                        nvpl_sparse_const_sp_mat_descr_t    mat_A,
                        nvpl_sparse_const_dn_vec_descr_t    vec_X,
                        nvpl_sparse_dn_vec_descr_t          vec_Y,
                        nvpl_sparse_data_type_t             compute_type,
                        nvpl_sparse_spsv_alg_t              alg,
                        nvpl_sparse_spsv_descr_t            spsv_descr,
                        size_t*                             buffer_size);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_spsv_analysis(nvpl_sparse_handle_t              handle,
                      nvpl_sparse_operation_t               op_A,
                      const void*                           alpha,
                      nvpl_sparse_const_sp_mat_descr_t      mat_A,
                      nvpl_sparse_const_dn_vec_descr_t      vec_X,
                      nvpl_sparse_dn_vec_descr_t            vec_Y,
                      nvpl_sparse_data_type_t               compute_type,
                      nvpl_sparse_spsv_alg_t                alg,
                      nvpl_sparse_spsv_descr_t              spsv_descr,
                      void*                                 external_buffer);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_spsv_solve(nvpl_sparse_handle_t                 handle,
                   nvpl_sparse_operation_t                  op_A,
                   const void*                              alpha,
                   nvpl_sparse_const_sp_mat_descr_t         mat_A,
                   nvpl_sparse_const_dn_vec_descr_t         vec_X,
                   nvpl_sparse_dn_vec_descr_t               vec_Y,
                   nvpl_sparse_data_type_t                  compute_type,
                   nvpl_sparse_spsv_alg_t                   alg,
                   nvpl_sparse_spsv_descr_t                 spsv_descr);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_spsv_update_matrix(nvpl_sparse_handle_t         handle,
				          nvpl_sparse_spsv_descr_t          spsv_descr,
                          void*                             new_values,
                          nvpl_sparse_spsv_update_t         update_part);



// #############################################################################
// # SPARSE TRIANGULAR MATRIX SOLVE
// #############################################################################

typedef enum {
    NVPL_SPARSE_SPSM_ALG_DEFAULT = 0,
} nvpl_sparse_spsmAlg_t;

struct nvpl_sparse_spsm_descr;
typedef struct nvpl_sparse_spsm_descr* nvpl_sparse_spsm_descr_t;

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_spsm_create_descr(nvpl_sparse_spsm_descr_t* descr);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_spsm_destroy_descr(nvpl_sparse_spsm_descr_t descr);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_spsm_buffer_size(nvpl_sparse_handle_t           handle,
                    nvpl_sparse_operation_t                 op_A,
                        nvpl_sparse_operation_t             op_B,
                        const void*                         alpha,
                        nvpl_sparse_const_sp_mat_descr_t    mat_A,
                        nvpl_sparse_const_dn_mat_descr_t    mat_B,
                        nvpl_sparse_dn_mat_descr_t          matC,
                        nvpl_sparse_data_type_t             compute_type,
                        nvpl_sparse_spsmAlg_t               alg,
                        nvpl_sparse_spsm_descr_t            spsm_descr,
                        size_t*                             buffer_size);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_spsm_analysis(nvpl_sparse_handle_t              handle,
                      nvpl_sparse_operation_t               op_A,
                      nvpl_sparse_operation_t               op_B,
                      const void*                           alpha,
                      nvpl_sparse_const_sp_mat_descr_t      mat_A,
                      nvpl_sparse_const_dn_mat_descr_t      mat_B,
                      nvpl_sparse_dn_mat_descr_t            matC,
                      nvpl_sparse_data_type_t               compute_type,
                      nvpl_sparse_spsmAlg_t                 alg,
                      nvpl_sparse_spsm_descr_t              spsm_descr,
                      void*                                 external_buffer);

nvpl_sparse_status_t NVPL_SPARSE_API
nvpl_sparse_spsm_solve(nvpl_sparse_handle_t                 handle,
                   nvpl_sparse_operation_t                  op_A,
                   nvpl_sparse_operation_t                  op_B,
                   const void*                              alpha,
                   nvpl_sparse_const_sp_mat_descr_t         mat_A,
                   nvpl_sparse_const_dn_mat_descr_t         mat_B,
                   nvpl_sparse_dn_mat_descr_t               matC,
                   nvpl_sparse_data_type_t                  compute_type,
                   nvpl_sparse_spsmAlg_t                    alg,
                   nvpl_sparse_spsm_descr_t                 spsm_descr);



#if defined(__cplusplus)
} // extern "C"
#endif // defined(__cplusplus)

#undef NVPL_SPARSE_DEPRECATED

#endif // !defined(NVPL_SPARSE_H_)

