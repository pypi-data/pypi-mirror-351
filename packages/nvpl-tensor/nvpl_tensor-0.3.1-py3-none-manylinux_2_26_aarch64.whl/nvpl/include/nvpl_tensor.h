/*
 * Copyright (c) 2019-23, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
 *
 * NVIDIA CORPORATION and its licensors retain all intellectual property
 * and proprietary rights in and to this software, related documentation
 * and any modifications thereto.  Any use, reproduction, disclosure or
 * distribution of this software and related documentation without an express
 * license agreement from NVIDIA CORPORATION is strictly prohibited.
 */


/**
 * @file
 * @brief This file contains all public function declarations of the nvplTENSOR
 * library.
 */
#pragma once

#define NVPLTENSOR_MAJOR 0 //!< nvplTensor major version.
#define NVPLTENSOR_MINOR 3 //!< nvplTensor minor version.
#define NVPLTENSOR_PATCH 0 //!< nvplTensor patch version.
#define NVPLTENSOR_VERSION (NVPLTENSOR_MAJOR * 10000 + NVPLTENSOR_MINOR * 100 + NVPLTENSOR_PATCH)

#include <stdint.h>
#include <stdio.h>

#include <nvpl_tensor/types.h>
#if defined(__cplusplus)
extern "C" {
#endif /* __cplusplus */

/**
 * \mainpage nvplTENSOR: Part of NVIDIA Performance Libraries for Tensor primitives
 *
 * \section intro Introduction
 *
 * \subsection nomen Nomenclature
 *
 * The term tensor refers to an \b order-n (a.k.a.,
 * n-dimensional) array. One can think of tensors as a generalization of
 * matrices to higher \b orders.

 * For example, scalars, vectors, and matrices are
 * order-0, order-1, and order-2 tensors, respectively.
 *
 * An order-n tensor has n \b modes. Each mode has an \b extent (a.k.a. size).
 * Each mode you can specify a \b stride s > 0. This \b stride
 * describes offset of two logically consecutive elements in physical (i.e., linearized) memory.
 * This is similar to the leading-dimension in BLAS.

 * nvplTENSOR, by default, adheres to a generalized \b column-major data layout.
 * For example: \f$A_{a,b,c} \in {R}^{4\times 8 \times 12}\f$
 * is an order-3 tensor with the extent of the a-mode, b-mode, and c-mode
 * respectively being 4, 8, and 12. If not explicitly specified, the strides are
 * assumed to be: stride(a) = 1, stride(b) = extent(a), stride(c) = extent(a) *
 * extent(b).

 * For a general order-n tensor \f$A_{i_1,i_2,...,i_n}\f$ we require that the strides do
 * not lead to overlapping memory accesses; for instance, \f$stride(i_1) \geq 1\f$, and
 * \f$stride(i_l) \geq stride(i_{l-1}) * extent(i_{l-1})\f$.

 * We say that a tensor is \b packed if it is contiguously stored in memory along all
 * modes. That is, \f$ stride(i_1) = 1\f$ and \f$stride(i_l) =stride(i_{l-1}) *
 * extent(i_{l-1})\f$).
 *
 * \subsection einsum Einstein Notation
 * We adhere to the "Einstein notation": Modes that appear in the input
 * tensors, and that do not appear in the output tensor, are implicitly
 * contracted.
 *
 * \section api API Reference
 * For details on the API please refer to \ref nvpltensor.h and \ref types.h.
 *
 */

/**
 * \brief Initializes the nvplTENSOR library and allocates the memory for the library context.
 *
 * The user is responsible for calling  \ref nvpltensorDestroy to free the resources associated
 * with the handle.
 *
 * \param[out] handle Pointer to nvpltensorHandle_t
 *
 * \retval NVPLTENSOR_STATUS_SUCCESS on success and an error code otherwise
 * \remarks blocking, no reentrant, and thread-safe
 */
nvpltensorStatus_t nvpltensorCreate(nvpltensorHandle_t* handle);

/**
 * \brief Frees all resources related to the provided library handle.
 *
 * \param[in,out] handle Pointer to nvpltensorHandle_t
 *
 * \retval NVPLTENSOR_STATUS_SUCCESS on success and an error code otherwise
 * \remarks blocking, no reentrant, and thread-safe
 */
nvpltensorStatus_t nvpltensorDestroy(nvpltensorHandle_t handle);

/**
 * \brief Creates a tensor descriptor.
 *
 * \details This allocates a small amount of host-memory.
 *
 * The user is responsible for calling nvpltensorDestroyTensorDescriptor() to free the associated resources once the tensor descriptor is no longer used.
 *
 * \param[in] handle Opaque handle holding nvplTENSOR's library context.
 * \param[out] desc Pointer to the address where the allocated tensor descriptor object will be stored.
 * \param[in] numModes Number of modes.
 * \param[in] extent Extent of each mode (must be larger than zero).
 * \param[in] stride stride[i] denotes the displacement (stride) between two consecutive elements in the ith-mode.
 *            If stride is NULL, a packed generalized column-major memory
 *            layout is assumed (i.e., the strides increase monotonically from left to
 *            right). Each stride must be larger than zero; to be precise, a stride of zero can be
 *            achieved by omitting this mode entirely; for instance instead of writing
 *            C[a,b] = A[b,a] with strideA(a) = 0, you can write C[a,b] = A[b] directly;
 *            nvplTENSOR will then automatically infer that the a-mode in A should be broadcasted.
 * \param[in] dataType Data type of the stored entries.
 * \param[in] alignmentRequirement Alignment (in bytes) to the base pointer that will be used in conjunction with this tensor descriptor.
 *
 * \pre extent and stride arrays must each contain at least sizeof(int64_t) * numModes bytes
 * \retval NVPLTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval NVPLTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval NVPLTENSOR_STATUS_NOT_SUPPORTED if the requested descriptor is not supported (e.g., due to non-supported data type).
 * \retval NVPLTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 * \remarks non-blocking, no reentrant, and thread-safe
 */
nvpltensorStatus_t nvpltensorCreateTensorDescriptor(const nvpltensorHandle_t handle,
                                              nvpltensorTensorDescriptor_t* desc,
                                              const uint32_t numModes,
                                              const int64_t extent[],
                                              const int64_t stride[],
                                              nvpltensorDataType_t dataType,
                                              uint32_t alignmentRequirement);

/**
 * \brief Frees all resources related to the provided tensor descriptor.
 *
 * \param[in,out] desc The nvpltensorTensorDescriptor_t object that will be deallocated.
 *
 * \retval NVPLTENSOR_STATUS_SUCCESS on success and an error code otherwise
 * \remarks blocking, no reentrant, and thread-safe
 */
nvpltensorStatus_t nvpltensorDestroyTensorDescriptor(nvpltensorTensorDescriptor_t desc);

/**
 * \brief This function creates an operation descriptor that encodes an elementwise trinary operation.
 *
 * \details Said trinary operation has the following general form:
 * \f[ D_{\Pi^C(i_0,i_1,...,i_n)} = \Phi_{ABC}(\Phi_{AB}(\alpha op_A(A_{\Pi^A(i_0,i_1,...,i_n)}), \beta op_B(B_{\Pi^B(i_0,i_1,...,i_n)})), \gamma op_C(C_{\Pi^C(i_0,i_1,...,i_n)})) \f]
 *
 * Where
 *    - A,B,C,D are multi-mode tensors (of arbitrary data types).
 *    - \f$\Pi^A, \Pi^B, \Pi^C \f$ are permutation operators that permute the modes of A, B, and C respectively.
 *    - \f$op_{A},op_{B},op_{C}\f$ are unary element-wise operators (e.g., IDENTITY, CONJUGATE).
 *    - \f$\Phi_{ABC}, \Phi_{AB}\f$ are binary element-wise operators (e.g., ADD, MUL, MAX, MIN).
 *
 * Notice that the broadcasting (of a mode) can be achieved by simply omitting that mode from the respective tensor.
 *
 * Moreover, modes may appear in any order, giving users a greater flexibility. The only <b>restrictions</b> are:
 *    - modes that appear in A or B _must_ also appear in the output tensor; a mode that only appears in the input would be contracted and such an operation would be covered by either \ref nvpltensorContract or \ref nvpltensorReduce.
 *    - each mode may appear in each tensor at most once.
 *
 * Input tensors may be read even if the value
 * of the corresponding scalar is zero.
 *
 * Examples:
 *    - \f$ D_{a,b,c,d} = A_{b,d,a,c}\f$
 *    - \f$ D_{a,b,c,d} = 2.2 * A_{b,d,a,c} + 1.3 * B_{c,b,d,a}\f$
 *    - \f$ D_{a,b,c,d} = 2.2 * A_{b,d,a,c} + 1.3 * B_{c,b,d,a} + C_{a,b,c,d}\f$
 *    - \f$ D_{a,b,c,d} = min((2.2 * A_{b,d,a,c} + 1.3 * B_{c,b,d,a}), C_{a,b,c,d})\f$
 *
 * Call \ref nvpltensorElementwiseTrinaryExecute to perform the actual operation.
 *
 * Please use \ref nvpltensorDestroyOperationDescriptor to deallocated the descriptor once it is no longer used.
 *
 * Supported data-type combinations are:
 *
 * \verbatim embed:rst:leading-asterisk
 * +--------------------+--------------------+--------------------+-------------------------------+
 * |     typeA          |     typeB          |    typeC           |  descCompute                  |
 * +====================+====================+====================+===============================+
 * | `NVPLTENSOR_R_32F` | `NVPLTENSOR_R_32F` | `NVPLTENSOR_R_32F` | `NVPLTENSOR_COMPUTE_DESC_32F` |
 * +--------------------+--------------------+--------------------+-------------------------------+
 * | `NVPLTENSOR_R_64F` | `NVPLTENSOR_R_64F` | `NVPLTENSOR_R_64F` | `NVPLTENSOR_COMPUTE_DESC_64F` |
 * +--------------------+--------------------+--------------------+-------------------------------+
 * | `NVPLTENSOR_C_32F` | `NVPLTENSOR_C_32F` | `NVPLTENSOR_C_32F` | `NVPLTENSOR_COMPUTE_DESC_32F` |
 * +--------------------+--------------------+--------------------+-------------------------------+
 * | `NVPLTENSOR_C_64F` | `NVPLTENSOR_C_64F` | `NVPLTENSOR_C_64F` | `NVPLTENSOR_COMPUTE_DESC_64F` |
 * +--------------------+--------------------+--------------------+-------------------------------+
 * \endverbatim
 *
 * \param[in] handle Opaque handle holding nvplTENSOR's library context.
 * \param[out] desc This opaque struct gets allocated and filled with the information that encodes the requested elementwise operation.
 * \param[in] descA A descriptor that holds the information about the data type, modes, and strides of A.
 * \param[in] modeA Array of size descA->numModes that holds the names of the modes of A (e.g., if \f$A_{a,b,c}\f$ then modeA = {'a','b','c'}). The modeA[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to \ref nvpltensorCreateTensorDescriptor.
 * \param[in] opA Unary operator that will be applied to each element of A before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descB A descriptor that holds information about the data type, modes, and strides of B.
 * \param[in] modeB Array of size descB->numModes that holds the names of the modes of B. modeB[i] corresponds to extent[i] and stride[i] of the \ref nvpltensorCreateTensorDescriptor
 * \param[in] opB Unary operator that will be applied to each element of B before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descC A descriptor that holds information about the data type, modes, and strides of C.
 * \param[in] modeC Array of size descC->numModes that holds the names of the modes of C. The modeC[i] corresponds to extent[i] and stride[i] of the \ref nvpltensorCreateTensorDescriptor.
 * \param[in] opC Unary operator that will be applied to each element of C before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descD A descriptor that holds information about the data type, modes, and strides of D. Notice that we currently request descD and descC to be identical.
 * \param[in] modeD Array of size descD->numModes that holds the names of the modes of D. The modeD[i] corresponds to extent[i] and stride[i] of the \ref nvpltensorCreateTensorDescriptor.
 * \param[in] opAB Element-wise binary operator (see \f$\Phi_{AB}\f$ above).
 * \param[in] opABC Element-wise binary operator (see \f$\Phi_{ABC}\f$ above).
 * \param[in] descCompute Determines the precision in which this operations is performed.
 * \retval NVPLTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval NVPLTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval NVPLTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 * \remarks calls asynchronous functions, no reentrant, and thread-safe
 */
nvpltensorStatus_t nvpltensorCreateElementwiseTrinary(
                 const nvpltensorHandle_t handle, nvpltensorOperationDescriptor_t* desc,
                 const nvpltensorTensorDescriptor_t descA, const int32_t modeA[], nvpltensorOperator_t opA,
                 const nvpltensorTensorDescriptor_t descB, const int32_t modeB[], nvpltensorOperator_t opB,
                 const nvpltensorTensorDescriptor_t descC, const int32_t modeC[], nvpltensorOperator_t opC,
                 const nvpltensorTensorDescriptor_t descD, const int32_t modeD[],
                 nvpltensorOperator_t opAB, nvpltensorOperator_t opABC,
                 const nvpltensorComputeDescriptor_t descCompute);

/**
 * \brief Performs an element-wise tensor operation for three input tensors (see \ref nvpltensorCreateElementwiseTrinary)
 *
 * \details This function performs a element-wise tensor operation of the form:
 * \f[ D_{\Pi^C(i_0,i_1,...,i_n)} = \Phi_{ABC}(\Phi_{AB}(\alpha op_A(A_{\Pi^A(i_0,i_1,...,i_n)}), \beta op_B(B_{\Pi^B(i_0,i_1,...,i_n)})), \gamma op_C(C_{\Pi^C(i_0,i_1,...,i_n)})) \f]
 *
 * See \ref nvpltensorCreateElementwiseTrinary() for details.
 *
 * \param[in] handle Opaque handle holding nvplTENSOR's library context.
 * \param[in] plan Opaque handle holding all information about the desired elementwise operation (created by \ref nvpltensorCreateElementwiseTrinary followed by \ref nvpltensorCreatePlan).
 * \param[in] alpha Pointer to the memory storing scaling factor for A (see \ref nvpltensorOperationDescriptorGetAttribute(desc, NVPLTENSOR_OPERATION_SCALAR_TYPE) to query the expected data type). If alpha is zero, A is not read and the corresponding unary operator is not applied.
 * \param[in] A Pointer to the memory storing multi-mode tensor (described by `descA` as part of \ref nvpltensorCreateElementwiseTrinary).
 * \param[in] beta Pointer to the memory storing scaling factor for B (see \ref nvpltensorOperationDescriptorGetAttribute(desc, NVPLTENSOR_OPERATION_SCALAR_TYPE) to query the expected data type). If beta is zero, B is not read and the corresponding unary operator is not applied.
 * \param[in] B Pointer to the memory storing multi-mode tensor (described by `descB` as part of \ref nvpltensorCreateElementwiseTrinary).
 * \param[in] gamma Pointer to the memory storing scaling factor for C (see \ref nvpltensorOperationDescriptorGetAttribute(desc, NVPLTENSOR_OPERATION_SCALAR_TYPE) to query the expected data type). If gamma is zero, C is not read and the corresponding unary operator is not applied.
 * \param[in] C Pointer to the memory storing multi-mode tensor (described by `descC` as part of \ref nvpltensorCreateElementwiseTrinary).
 * \param[out] D Pointer to the memory storing multi-mode tensor (described by `descD` as part of \ref nvpltensorCreateElementwiseTrinary). `C` and `D` may be identical, if and only if `descC == descD`.
 * \retval NVPLTENSOR_STATUS_NOT_SUPPORTED if the combination of data types or operations is not supported
 * \retval NVPLTENSOR_STATUS_INVALID_VALUE if tensor dimensions or modes have an illegal value
 * \retval NVPLTENSOR_STATUS_SUCCESS The operation completed successfully without error
 * \retval NVPLTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \remarks calls asynchronous functions, no reentrant, and thread-safe
 */
nvpltensorStatus_t nvpltensorElementwiseTrinaryExecute(
                 const nvpltensorHandle_t handle, const nvpltensorPlan_t plan,
                 const void* alpha, const void* A,
                 const void* beta,  const void* B,
                 const void* gamma, const void* C,
                                          void* D);

/**
 * \brief This function creates an operation descriptor for an elementwise binary operation.
 *
 * \details The binary operation has the following general form:
 * \f[ D_{\Pi^C(i_0,i_1,...,i_n)} = \Phi_{AC}(\alpha \Psi_A(A_{\Pi^A(i_0,i_1,...,i_n)}), \gamma \Psi_C(C_{\Pi^C(i_0,i_1,...,i_n)})) \f]
 *
 * Call \ref nvpltensorElementwiseBinaryExecute to perform the actual operation.
 *
 * Supported data-type combinations are:
 *
 * \verbatim embed:rst:leading-asterisk
 * +--------------------+--------------------+-------------------------------+
 * |     typeA          |    typeC           |  descCompute                  |
 * +====================+====================+===============================+
 * | `NVPLTENSOR_R_32F` | `NVPLTENSOR_R_32F` | `NVPLTENSOR_COMPUTE_DESC_32F` |
 * +--------------------+--------------------+-------------------------------+
 * | `NVPLTENSOR_R_64F` | `NVPLTENSOR_R_64F` | `NVPLTENSOR_COMPUTE_DESC_64F` |
 * +--------------------+--------------------+-------------------------------+
 * | `NVPLTENSOR_C_32F` | `NVPLTENSOR_C_32F` | `NVPLTENSOR_COMPUTE_DESC_32F` |
 * +--------------------+--------------------+-------------------------------+
 * | `NVPLTENSOR_C_64F` | `NVPLTENSOR_C_64F` | `NVPLTENSOR_COMPUTE_DESC_64F` |
 * +--------------------+--------------------+-------------------------------+
 * \endverbatim
 *
 * \param[in] handle Opaque handle holding nvplTENSOR's library context.
 * \param[out] desc This opaque struct gets allocated and filled with the information that encodes the requested elementwise operation.
 * \param[in] descA The descriptor that holds the information about the data type, modes, and strides of A.
 * \param[in] modeA Array of size descA->numModes that holds the names of the modes of A (e.g., if A_{a,b,c} => modeA = {'a','b','c'}). The modeA[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to \ref nvpltensorCreateTensorDescriptor.
 * \param[in] opA Unary operator that will be applied to each element of A before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descC The descriptor that holds information about the data type, modes, and strides of C.
 * \param[in] modeC Array of size descC->numModes that holds the names of the modes of C. The modeC[i] corresponds to extent[i] and stride[i] of the \ref nvpltensorCreateTensorDescriptor.
 * \param[in] opC Unary operator that will be applied to each element of C before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descD The descriptor that holds information about the data type, modes, and strides of D. Notice that we currently request descD and descC to be identical.
 * \param[in] modeD Array of size descD->numModes that holds the names of the modes of D. The modeD[i] corresponds to extent[i] and stride[i] of the \ref nvpltensorCreateTensorDescriptor.
 * \param[in] opAC Element-wise binary operator (see \f$\Phi_{AC}\f$ above).
 * \param[in] descCompute Determines the precision in which this operations is performed.
 * \retval NVPLTENSOR_STATUS_NOT_SUPPORTED if the combination of data types or operations is not supported
 * \retval NVPLTENSOR_STATUS_INVALID_VALUE if tensor dimensions or modes have an illegal value
 * \retval NVPLTENSOR_STATUS_SUCCESS The operation completed successfully without error
 * \retval NVPLTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \remarks calls asynchronous functions, no reentrant, and thread-safe
 */
nvpltensorStatus_t nvpltensorCreateElementwiseBinary(
                 const nvpltensorHandle_t handle, nvpltensorOperationDescriptor_t* desc,
                 const nvpltensorTensorDescriptor_t descA, const int32_t modeA[], nvpltensorOperator_t opA,
                 const nvpltensorTensorDescriptor_t descC, const int32_t modeC[], nvpltensorOperator_t opC,
                 const nvpltensorTensorDescriptor_t descD, const int32_t modeD[],
                 nvpltensorOperator_t opAC,
                 const nvpltensorComputeDescriptor_t descCompute);

/**
 * \brief Performs an element-wise tensor operation for two input tensors (see \ref nvpltensorCreateElementwiseBinary)
 *
 * \details This function performs a element-wise tensor operation of the form:
 * \f[ D_{\Pi^C(i_0,i_1,...,i_n)} = \Phi_{AC}(\alpha \Psi_A(A_{\Pi^A(i_0,i_1,...,i_n)}), \gamma \Psi_C(C_{\Pi^C(i_0,i_1,...,i_n)})) \f]
 *
 * See \ref nvpltensorCreateElementwiseBinary() for details.
 *
 * \param[in] handle Opaque handle holding nvplTENSOR's library context.
 * \param[in] plan Opaque handle holding all information about the desired elementwise operation (created by \ref nvpltensorCreateElementwiseBinary followed by \ref nvpltensorCreatePlan).
 * \param[in] alpha Pointer to the memory storing scaling factor for A (see \ref nvpltensorOperationDescriptorGetAttribute(desc, NVPLTENSOR_OPERATION_SCALAR_TYPE) to query the expected data type). If alpha is zero, A is not read and the corresponding unary operator is not applied.
 * \param[in] A Pointer to the memory storing multi-mode tensor (described by `descA` as part of \ref nvpltensorCreateElementwiseBinary).
 * \param[in] gamma Pointer to the memory storing scaling factor for C (see \ref nvpltensorOperationDescriptorGetAttribute(desc, NVPLTENSOR_OPERATION_SCALAR_TYPE) to query the expected data type). If gamma is zero, C is not read and the corresponding unary operator is not applied.
 * \param[in] C Pointer to the memory storing multi-mode tensor (described by `descC` as part of \ref nvpltensorCreateElementwiseBinary).
 * \param[out] D Pointer to the memory storing multi-mode tensor (described by `descD` as part of \ref nvpltensorCreateElementwiseBinary). `C` and `D` may be identical, if and only if `descC == descD`.
 * \retval NVPLTENSOR_STATUS_NOT_SUPPORTED if the combination of data types or operations is not supported
 * \retval NVPLTENSOR_STATUS_INVALID_VALUE if tensor dimensions or modes have an illegal value
 * \retval NVPLTENSOR_STATUS_SUCCESS The operation completed successfully without error
 * \retval NVPLTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \remarks calls asynchronous functions, no reentrant, and thread-safe
 */
nvpltensorStatus_t nvpltensorElementwiseBinaryExecute(
                 const nvpltensorHandle_t handle, const nvpltensorPlan_t plan,
                 const void* alpha, const void* A,
                 const void* gamma, const void* C,
                                          void* D);

/**
 * \brief This function creates an operation descriptor for a tensor permutation.
 *
 * \details The tensor permutation has the following general form:
 * \f[ B_{\Pi^B(i_0,i_1,...,i_n)} = \alpha op_A(A_{\Pi^A(i_0,i_1,...,i_n)}) \f]
 *
 * Consequently, this function performs an out-of-place tensor permutation and is a specialization of \ref nvpltensorCreateElementwiseBinary.
 *
 * Where
 *    - A and B are multi-mode tensors (of arbitrary data types),
 *    - \f$\Pi^A, \Pi^B\f$ are permutation operators that permute the modes of A, B respectively,
 *    - \f$op_A\f$ is an unary element-wise operators (e.g., IDENTITY, SQR, CONJUGATE), and
 *    - \f$\Psi\f$ is specified in the tensor descriptor descA.
 *
 * Broadcasting (of a mode) can be achieved by simply omitting that mode from the respective tensor.
 *
 * Modes may appear in any order. The only <b>restrictions</b> are:
 *    - modes that appear in A _must_ also appear in the output tensor.
 *    - each mode may appear in each tensor at most once.
 *
 * Supported data-type combinations are:
 *
 * \verbatim embed:rst:leading-asterisk
 * +--------------------+--------------------+-------------------------------+
 * |     typeA          |     typeB          |  descCompute                  |
 * +====================+====================+===============================+
 * | `NVPLTENSOR_R_32F` | `NVPLTENSOR_R_32F` | `NVPLTENSOR_COMPUTE_DESC_32F` |
 * +--------------------+--------------------+-------------------------------+
 * | `NVPLTENSOR_R_64F` | `NVPLTENSOR_R_64F` | `NVPLTENSOR_COMPUTE_DESC_64F` |
 * +--------------------+--------------------+-------------------------------+
 * | `NVPLTENSOR_C_32F` | `NVPLTENSOR_C_32F` | `NVPLTENSOR_COMPUTE_DESC_32F` |
 * +--------------------+--------------------+-------------------------------+
 * | `NVPLTENSOR_C_64F` | `NVPLTENSOR_C_64F` | `NVPLTENSOR_COMPUTE_DESC_64F` |
 * +--------------------+--------------------+-------------------------------+
 * \endverbatim
 *
 * \param[in] handle Opaque handle holding nvplTENSOR's library context.
 * \param[out] desc This opaque struct gets allocated and filled with the information that encodes the requested permutation.
 * \param[in] descA The descriptor that holds information about the data type, modes, and strides of A.
 * \param[in] modeA Array of size descA->numModes that holds the names of the modes of A (e.g., if A_{a,b,c} => modeA = {'a','b','c'})
 * \param[in] opA Unary operator that will be applied to each element of A before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descB The descriptor that holds information about the data type, modes, and strides of B.
 * \param[in] modeB Array of size descB->numModes that holds the names of the modes of B
 * \param[in] descCompute Determines the precision in which this operations is performed.
 * \retval NVPLTENSOR_STATUS_NOT_SUPPORTED if the combination of data types or operations is not supported
 * \retval NVPLTENSOR_STATUS_INVALID_VALUE if tensor dimensions or modes have an illegal value
 * \retval NVPLTENSOR_STATUS_SUCCESS The operation completed successfully without error
 * \retval NVPLTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \remarks calls asynchronous functions, no reentrant, and thread-safe
 */
nvpltensorStatus_t nvpltensorCreatePermutation(
                 const nvpltensorHandle_t handle, nvpltensorOperationDescriptor_t* desc,
                 const nvpltensorTensorDescriptor_t descA, const int32_t modeA[], nvpltensorOperator_t opA,
                 const nvpltensorTensorDescriptor_t descB, const int32_t modeB[],
                 const nvpltensorComputeDescriptor_t descCompute);

/**
 * \brief Performs the tensor permutation that is encoded by `plan` (see \ref nvpltensorCreatePermutation).
 *
 * \details This function performs an elementwise tensor operation of the form:
 * \f[ B_{\Pi^B(i_0,i_1,...,i_n)} = \alpha \Psi(A_{\Pi^A(i_0,i_1,...,i_n)}) \f]
 *
 * Consequently, this function performs an out-of-place tensor permutation.
 *
 * Where
 *    - A and B are multi-mode tensors (of arbitrary data types),
 *    - \f$\Pi^A, \Pi^B\f$ are permutation operators that permute the modes of A, B respectively,
 *    - \f$\Psi\f$ is an unary element-wise operators (e.g., IDENTITY, SQR, CONJUGATE), and
 *    - \f$\Psi\f$ is specified in the tensor descriptor descA.
 *
 * \param[in] handle Opaque handle holding nvplTENSOR's library context.
 * \param[in] plan Opaque handle holding all information about the desired tensor reduction (created by \ref nvpltensorCreatePermutation followed by \ref nvpltensorCreatePlan).
 * \param[in] alpha Pointer to the memory storing scaling factor for A (see \ref nvpltensorOperationDescriptorGetAttribute(desc, NVPLTENSOR_OPERATION_SCALAR_TYPE)). If alpha is zero, A is not read and the corresponding unary operator is not applied.
 * \param[in] A Pointer to the memory storing multi-mode tensor (described by `descA` as part of \ref nvpltensorCreatePermutation).
 * \param[in,out] B Pointer to the memory storing multi-mode tensor (described by `descB` as part of \ref nvpltensorCreatePermutation).
 * \retval NVPLTENSOR_STATUS_NOT_SUPPORTED if the combination of data types or operations is not supported
 * \retval NVPLTENSOR_STATUS_INVALID_VALUE if tensor dimensions or modes have an illegal value
 * \retval NVPLTENSOR_STATUS_SUCCESS The operation completed successfully without error
 * \retval NVPLTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \remarks calls asynchronous functions, no reentrant, and thread-safe
 */
nvpltensorStatus_t nvpltensorPermute(
                 const nvpltensorHandle_t handle, const nvpltensorPlan_t plan,
                 const void* alpha, const void* A,
                                          void* B);

/**
 * \brief This function allocates a nvpltensorOperationDescriptor_t object that encodes a tensor contraction of the form \f$ D = \alpha \mathcal{A}  \mathcal{B} + \beta \mathcal{C} \f$.
 *
 * \details Allocates data for `desc` to be used to perform a tensor contraction of the form \f[ \mathcal{D}_{{modes}_\mathcal{D}} \gets \alpha op_\mathcal{A}(\mathcal{A}_{{modes}_\mathcal{A}}) op_\mathcal{B}(B_{{modes}_\mathcal{B}}) + \beta op_\mathcal{C}(\mathcal{C}_{{modes}_\mathcal{C}}). \f]
 *
 * See \ref nvpltensorCreatePlan (or \ref nvpltensorCreatePlanAutotuned) to create the plan
 * (i.e., to select the kernel) followed by a call to \ref nvpltensorContract to perform the
 * actual contraction.
 *
 * The user is responsible for calling \ref nvpltensorDestroyOperationDescriptor to free the resources associated
 * with the descriptor.
 *
 * Supported data-type combinations are:
 *
 * \verbatim embed:rst:leading-asterisk
 * +--------------------+--------------------+--------------------+-------------------------------+--------------------+
 * |     typeA          |     typeB          |     typeC          |        descCompute            |  typeScalar        |
 * +====================+====================+====================+===============================+====================+
 * | `NVPLTENSOR_R_32F` | `NVPLTENSOR_R_32F` | `NVPLTENSOR_R_32F` | `NVPLTENSOR_COMPUTE_DESC_32F` | `NVPLTENSOR_R_32F` |
 * +--------------------+--------------------+--------------------+-------------------------------+--------------------+
 * | `NVPLTENSOR_R_64F` | `NVPLTENSOR_R_64F` | `NVPLTENSOR_R_64F` | `NVPLTENSOR_COMPUTE_DESC_64F` | `NVPLTENSOR_R_64F` |
 * +--------------------+--------------------+--------------------+-------------------------------+--------------------+
 * | `NVPLTENSOR_C_32F` | `NVPLTENSOR_C_32F` | `NVPLTENSOR_C_32F` | `NVPLTENSOR_COMPUTE_DESC_32F` | `NVPLTENSOR_C_32F` |
 * +--------------------+--------------------+--------------------+-------------------------------+--------------------+
 * | `NVPLTENSOR_C_64F` | `NVPLTENSOR_C_64F` | `NVPLTENSOR_C_64F` | `NVPLTENSOR_COMPUTE_DESC_64F` | `NVPLTENSOR_C_64F` |
 * +--------------------+--------------------+--------------------+-------------------------------+--------------------+
 * \endverbatim
 *
 * \param[in] handle Opaque handle holding nvplTENSOR's library context.
 * \param[out] desc This opaque struct gets allocated and filled with the information that encodes
 * the tensor contraction operation.
 * \param[in] descA The descriptor that holds the information about the data type, modes and strides of A.
 * \param[in] modeA Array with 'nmodeA' entries that represent the modes of A. The modeA[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to nvpltensorInitTensorDescriptor.
 * \param[in] opA Unary operator that will be applied to each element of A before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descB The descriptor that holds information about the data type, modes, and strides of B.
 * \param[in] modeB Array with 'nmodeB' entries that represent the modes of B. The modeB[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to nvpltensorInitTensorDescriptor.
 * \param[in] opB Unary operator that will be applied to each element of B before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] modeC Array with 'nmodeC' entries that represent the modes of C. The modeC[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to nvpltensorInitTensorDescriptor.
 * \param[in] descC The escriptor that holds information about the data type, modes, and strides of C.
 * \param[in] opC Unary operator that will be applied to each element of C before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] modeD Array with 'nmodeD' entries that represent the modes of D (must be identical to modeC for now). The modeD[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to nvpltensorInitTensorDescriptor.
 * \param[in] descD The descriptor that holds information about the data type, modes, and strides of D (must be identical to `descC` for now).
 * \param[in] descCompute Datatype of for the intermediate computation of typeCompute T = A * B.
 * \retval NVPLTENSOR_STATUS_NOT_SUPPORTED if the combination of data types or operations is not supported
 * \retval NVPLTENSOR_STATUS_INVALID_VALUE if tensor dimensions or modes have an illegal value
 * \retval NVPLTENSOR_STATUS_SUCCESS The operation completed successfully without error
 * \retval NVPLTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 */
nvpltensorStatus_t nvpltensorCreateContraction(
                 const nvpltensorHandle_t handle, nvpltensorOperationDescriptor_t* desc,
                 const nvpltensorTensorDescriptor_t descA, const int32_t modeA[], nvpltensorOperator_t opA,
                 const nvpltensorTensorDescriptor_t descB, const int32_t modeB[], nvpltensorOperator_t opB,
                 const nvpltensorTensorDescriptor_t descC, const int32_t modeC[], nvpltensorOperator_t opC,
                 const nvpltensorTensorDescriptor_t descD, const int32_t modeD[],
                 const nvpltensorComputeDescriptor_t descCompute);

/**
 * \brief Frees all resources related to the provided descriptor.
 *
 * \param[in,out] desc The nvpltensorOperationDescriptor_t object that will be deallocated.
 *
 * \retval NVPLTENSOR_STATUS_SUCCESS on success and an error code otherwise
 * \remarks blocking, no reentrant, and thread-safe
 */
nvpltensorStatus_t nvpltensorDestroyOperationDescriptor(nvpltensorOperationDescriptor_t desc);

/**
 * \brief Set attribute of a nvpltensorOperationDescriptor_t object.
 *
 * \param[in] handle Opaque handle holding nvplTENSOR's library context.
 * \param[in,out] desc Operation descriptor that will be modified.
 * \param[in] attr Specifies the attribute that will be set.
 * \param[in] buf This buffer (of size `sizeInBytes`) determines the value to which `attr` will be set.
 * \param[in] sizeInBytes Size of buf (in bytes).
 * \retval NVPLTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval NVPLTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval NVPLTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 */
nvpltensorStatus_t nvpltensorOperationDescriptorSetAttribute(
        const nvpltensorHandle_t handle,
        nvpltensorOperationDescriptor_t desc,
        nvpltensorOperationDescriptorAttribute_t attr,
        const void *buf,
        size_t sizeInBytes);

/**
 * \brief This function retrieves an attribute of the provided nvpltensorOperationDescriptor_t object (see \ref nvpltensorOperationDescriptorAttribute_t).
 *
 * \param[in] handle Opaque handle holding nvplTENSOR's library context.
 * \param[in] desc The nvpltensorOperationDescriptor_t object whos attribute is queried.
 * \param[in] attr Specifies the attribute that will be retrieved.
 * \param[out] buf This buffer (of size sizeInBytes) will hold the requested attribute of the provided nvpltensorOperationDescriptor_t object.
 * \param[in] sizeInBytes Size of buf (in bytes); see \ref nvpltensorOperationDescriptorAttribute_t for the exact size.
 * \retval NVPLTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval NVPLTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval NVPLTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 */
nvpltensorStatus_t nvpltensorOperationDescriptorGetAttribute(
        const nvpltensorHandle_t handle,
        nvpltensorOperationDescriptor_t desc,
        nvpltensorOperationDescriptorAttribute_t attr,
        void *buf,
        size_t sizeInBytes);

/**
  * \brief Allocates the nvpltensorPlanPreference_t, enabling users to limit the applicable kernels for a given plan/operation.
  *
  * \param[in] handle Opaque handle holding nvplTENSOR's library context.
  * \param[out] pref Pointer to the structure holding the \ref nvpltensorPlanPreference_t allocated
  * by this function. See \ref nvpltensorPlanPreference_t.
  * \param[in] algo Allows users to select a specific algorithm. NVPLTENSOR_ALGO_DEFAULT lets the heuristic choose the algorithm. Any value >= 0 selects a specific GEMM-like algorithm
  *                 and deactivates the heuristic. If a specified algorithm is not supported NVPLTENSOR_STATUS_NOT_SUPPORTED is returned. See \ref nvpltensorAlgo_t for additional choices.
  * \param[in] jitMode Determines if nvplTENSOR is allowed to use JIT-compiled kernels (leading to a longer plan-creation phase); see \ref nvpltensorJitMode_t.
  */
nvpltensorStatus_t nvpltensorCreatePlanPreference(
                               const nvpltensorHandle_t handle,
                               nvpltensorPlanPreference_t* pref,
                               nvpltensorAlgo_t algo,
                               nvpltensorJitMode_t jitMode);

/**
 * \brief Frees all resources related to the provided preference.
 *
 * \param[in,out] pref The nvpltensorPlanPreference_t object that will be deallocated.
 *
 * \retval NVPLTENSOR_STATUS_SUCCESS on success and an error code otherwise
 * \remarks blocking, no reentrant, and thread-safe
 */
nvpltensorStatus_t nvpltensorDestroyPlanPreference(nvpltensorPlanPreference_t pref);

/**
 * \brief Set attribute of a nvpltensorPlanPreference_t object.
 *
 * \param[in] handle Opaque handle holding nvplTENSOR's library context.
 * \param[in,out] pref This opaque struct restricts the search space of viable candidates.
 * \param[in] attr Specifies the attribute that will be set.
 * \param[in] buf This buffer (of size sizeInBytes) determines the value to which `attr`
 * will be set.
 * \param[in] sizeInBytes Size of buf (in bytes); see \ref nvpltensorPlanPreferenceAttribute_t for the exact size.
 * \retval NVPLTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval NVPLTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval NVPLTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 */
nvpltensorStatus_t nvpltensorPlanPreferenceSetAttribute(
        const nvpltensorHandle_t handle,
        nvpltensorPlanPreference_t pref,
        nvpltensorPlanPreferenceAttribute_t attr,
        const void *buf,
        size_t sizeInBytes);

/**
 * \brief Retrieves information about an already-created plan (see \ref nvpltensorPlanAttribute_t)
 *
 * \param[in] plan Denotes an already-created plan (e.g., via \ref nvpltensorCreatePlan or \ref nvpltensorCreatePlanAutotuned)
 * \param[in] attr Requested attribute.
 * \param[out] buf On successful exit: Holds the information of the requested attribute.
 * \param[in] sizeInBytes size of `buf` in bytes.
 * \retval NVPLTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval NVPLTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 */
nvpltensorStatus_t nvpltensorPlanGetAttribute(const nvpltensorHandle_t handle,
        const nvpltensorPlan_t plan,
        nvpltensorPlanAttribute_t attr,
        void* buf,
        size_t sizeInBytes);

/**
 * \brief Determines the required workspaceSize for the given operation encoded by `desc`.
 *
 * \param[in] handle Opaque handle holding nvplTENSOR's library context.
 * \param[in] desc This opaque struct encodes the operation.
 * \param[in] planPref This opaque struct restricts the space of viable candidates.
 * \param[in] workspacePref This parameter influences the size of the workspace; see \ref nvpltensorWorksizePreference_t for details.
 * \param[out] workspaceSizeEstimate The workspace size (in bytes) that is required for the given operation.
 * \retval NVPLTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval NVPLTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval NVPLTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 */
nvpltensorStatus_t nvpltensorEstimateWorkspaceSize(const nvpltensorHandle_t handle,
                                          const nvpltensorOperationDescriptor_t desc,
                                          const nvpltensorPlanPreference_t planPref,
                                          const nvpltensorWorksizePreference_t workspacePref,
                                          uint64_t *workspaceSizeEstimate);

/**
 * \brief This function allocates a nvpltensorPlan_t object, selects an appropriate kernel for a given operation (encoded by `desc`) and prepares a plan that encodes the execution.
 *
 * \details This function applies nvplTENSOR's heuristic to select a candidate/kernel for a
 * given operation (created by either \ref nvpltensorCreateContraction, \ref nvpltensorCreateReduction, \ref nvpltensorCreatePermutation, \ref
 * nvpltensorCreateElementwiseBinary, or \ref nvpltensorCreateElementwiseTrinary). The created plan can then be
 * be passed to either \ref nvpltensorContract, \ref nvpltensorReduce, \ref nvpltensorPermute, \ref
 * nvpltensorElementwiseBinaryExecute, or \ref nvpltensorElementwiseTrinaryExecute to perform
 * the actual operation.
 *
 * \param[in] handle Opaque handle holding nvplTENSOR's library context.
 * \param[out] plan Pointer to the data structure created by this function that holds all information (e.g., selected
 * kernel) necessary to perform the desired operation.
 * \param[in] desc This opaque struct encodes the given operation (see \ref nvpltensorCreateContraction, \ref nvpltensorCreateReduction, \ref nvpltensorCreatePermutation, \ref
 * nvpltensorCreateElementwiseBinary, or \ref nvpltensorCreateElementwiseTrinary).
 * \param[in] pref This opaque struct is used to restrict the space of applicable candidates/kernels (see \ref nvpltensorCreatePlanPreference or \ref nvpltensorPlanPreferenceAttribute_t). May be `nullptr`, in that case default choices are assumed.
 * \param[in] workspaceSizeLimit Denotes the maximal workspace that the corresponding operation is allowed to use (see \ref nvpltensorEstimateWorkspaceSize)
 *
 * \retval NVPLTENSOR_STATUS_SUCCESS If a viable candidate has been found.
 * \retval NVPLTENSOR_STATUS_NOT_SUPPORTED If no viable candidate could be found.
 * \retval NVPLTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 * \retval NVPLTENSOR_STATUS_INSUFFICIENT_WORKSPACE if The provided workspace was insufficient.
 * \retval NVPLTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 */
nvpltensorStatus_t nvpltensorCreatePlan(
                               const nvpltensorHandle_t handle,
                               nvpltensorPlan_t* plan,
                               const nvpltensorOperationDescriptor_t desc,
                               const nvpltensorPlanPreference_t pref,
                               uint64_t workspaceSizeLimit);

/**
 * \brief Frees all resources related to the provided plan.
 *
 * \param[in,out] plan The nvpltensorPlan_t object that will be deallocated.
 * \retval NVPLTENSOR_STATUS_SUCCESS on success and an error code otherwise
 * \remarks blocking, no reentrant, and thread-safe
 */
nvpltensorStatus_t nvpltensorDestroyPlan(nvpltensorPlan_t plan);

/**
 * \brief This routine computes the tensor contraction \f$ D = alpha * A * B + beta * C \f$.
 *
 * \details \f[ \mathcal{D}_{{modes}_\mathcal{D}} \gets \alpha * \mathcal{A}_{{modes}_\mathcal{A}} B_{{modes}_\mathcal{B}} + \beta \mathcal{C}_{{modes}_\mathcal{C}} \f]
 *
 * \param[in] handle Opaque handle holding nvplTENSOR's library context.
 * \param[in] plan Opaque handle holding the contraction execution plan (created by \ref nvpltensorCreateContraction followed by \ref nvpltensorCreatePlan).
 * \param[in] alpha Pointer to the memory storing scaling for A*B. Its data type is determined by 'descCompute' (see \ref nvpltensorOperationDescriptorGetAttribute(desc, NVPLTENSOR_OPERATION_SCALAR_TYPE)).
 * \param[in] A Pointer to the memory storing multi-mode tensor (described by `descA` as part of \ref nvpltensorCreateContraction).
 * \param[in] B Pointer to the memory storing multi-mode tensor (described by `descB` as part of \ref nvpltensorCreateContraction).
 * \param[in] beta Scaling for C. Its data type is determined by 'descCompute' (see \ref nvpltensorOperationDescriptorGetAttribute(desc, NVPLTENSOR_OPERATION_SCALAR_TYPE)). Pointer to the host memory.
 * \param[in] C Pointer to the memory storing multi-mode tensor (described by `descC` as part of \ref nvpltensorCreateContraction).
 * \param[out] D Pointer to the memory storing multi-mode tensor (described by `descD` as part of \ref nvpltensorCreateContraction). `C` and `D` may be identical, if and only if `descC == descD`.
 * \param[out] workspace Optional parameter that may be NULL. This pointer provides additional workspace to the library for additional optimizations; the workspace must be aligned to 256 bytes.
 * \param[in] workspaceSize Size of the workspace array in bytes; please refer to \ref nvpltensorEstimateWorkspaceSize to query the required workspace. While \ref nvpltensorContract does not strictly require a workspace for the contraction, it is still recommended to provided some small workspace (e.g., 128 MB).
 *
 * \retval NVPLTENSOR_STATUS_NOT_SUPPORTED if operation is not supported.
 * \retval NVPLTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 * \retval NVPLTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval NVPLTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 */
nvpltensorStatus_t nvpltensorContract(
                 const nvpltensorHandle_t handle, const nvpltensorPlan_t plan,
                 const void* alpha, const void *A,
                                    const void *B,
                 const void* beta,  const void *C, void *D,
                 void* workspace, uint64_t workspaceSize);

/**
 * \brief Creates a nvpltensorOperatorDescriptor_t object that encodes a tensor reduction of the form \f$ D = alpha * opReduce(opA(A)) + beta * opC(C) \f$.
 *
 * \details
 * For example this function enables users to reduce an entire tensor to a scalar: C[] = alpha * A[i,j,k];
 *
 * This function is also able to perform partial reductions; for instance: C[i,j] = alpha * A[k,j,i]; in this case only elements along the k-mode are contracted.
 *
 * The binary opReduce operator provides extra control over what kind of a reduction
 * ought to be performed. For instance, setting opReduce to `NVPLTENSOR_OP_ADD` reduces element of A
 * via a summation while `NVPLTENSOR_OP_MAX` would find the largest element in A.
 *
 * Supported data-type combinations are:
 *
 * \verbatim embed:rst:leading-asterisk
 * +---------------------+---------------------+---------------------+-------------------------------+
 * |     typeA           |     typeB           |     typeC           |       typeCompute             |
 * +=====================+=====================+=====================+===============================+
 * | `NVPLTENSOR_R_32F`  | `NVPLTENSOR_R_32F`  | `NVPLTENSOR_R_32F`  | `NVPLTENSOR_COMPUTE_DESC_32F` |
 * +---------------------+---------------------+---------------------+-------------------------------+
 * | `NVPLTENSOR_R_64F`  | `NVPLTENSOR_R_64F`  | `NVPLTENSOR_R_64F`  | `NVPLTENSOR_COMPUTE_DESC_64F` |
 * +---------------------+---------------------+---------------------+-------------------------------+
 * | `NVPLTENSOR_C_32F`  | `NVPLTENSOR_C_32F`  | `NVPLTENSOR_C_32F`  | `NVPLTENSOR_COMPUTE_DESC_32F` |
 * +---------------------+---------------------+---------------------+-------------------------------+
 * | `NVPLTENSOR_C_64F`  | `NVPLTENSOR_C_64F`  | `NVPLTENSOR_C_64F`  | `NVPLTENSOR_COMPUTE_DESC_64F` |
 * +---------------------+---------------------+---------------------+-------------------------------+
 * \endverbatim
 *
 * \param[in] handle Opaque handle holding nvplTENSOR's library context.
 * \param[out] desc This opaque struct gets allocated and filled with the information that encodes
 * the requested tensor reduction operation.
 * \param[in] descA The descriptor that holds the information about the data type, modes and strides of A.
 * \param[in] modeA Array with 'nmodeA' entries that represent the modes of A. modeA[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to \ref nvpltensorCreateTensorDescriptor. Modes that only appear in modeA but not in modeC are reduced (contracted).
 * \param[in] opA Unary operator that will be applied to each element of A before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descC The descriptor that holds the information about the data type, modes and strides of C.
 * \param[in] modeC Array with 'nmodeC' entries that represent the modes of C. modeC[i] corresponds to extent[i] and stride[i] w.r.t. the arguments provided to \ref nvpltensorCreateTensorDescriptor.
 * \param[in] opC Unary operator that will be applied to each element of C before it is further processed. The original data of this tensor remains unchanged.
 * \param[in] descD Must be identical to descC for now.
 * \param[in] modeD Must be identical to modeC for now.
 * \param[in] opReduce binary operator used to reduce elements of A.
 * \param[in] typeCompute All arithmetic is performed using this data type (i.e., it affects the accuracy and performance).
 *
 * \retval NVPLTENSOR_STATUS_NOT_SUPPORTED if operation is not supported.
 * \retval NVPLTENSOR_STATUS_INVALID_VALUE if some input data is invalid (this typically indicates an user error).
 * \retval NVPLTENSOR_STATUS_SUCCESS The operation completed successfully.
 * \retval NVPLTENSOR_STATUS_NOT_INITIALIZED if the handle is not initialized.
 */
nvpltensorStatus_t nvpltensorCreateReduction(
                 const nvpltensorHandle_t handle, nvpltensorOperationDescriptor_t* desc,
                 const nvpltensorTensorDescriptor_t descA, const int32_t modeA[], nvpltensorOperator_t opA,
                 const nvpltensorTensorDescriptor_t descC, const int32_t modeC[], nvpltensorOperator_t opC,
                 const nvpltensorTensorDescriptor_t descD, const int32_t modeD[],
                 nvpltensorOperator_t opReduce, const nvpltensorComputeDescriptor_t descCompute);


/**
 * \brief Performs the tensor reduction that is encoded by `plan` (see \ref nvpltensorCreateReduction).
 *
 * \param[in] alpha Pointer to the memory storing scaling for A. Its data type is determined by 'descCompute' (see \ref nvpltensorOperationDescriptorGetAttribute(desc, NVPLTENSOR_OPERATION_SCALAR_TYPE)).
 * \param[in] A Pointer to the memory storing multi-mode tensor (described by `descA` as part of \ref nvpltensorCreateReduction).
 * \param[in] beta Pointer to the memory storing scaling for C. Its data type is determined by 'descCompute' (see \ref nvpltensorOperationDescriptorGetAttribute(desc, NVPLTENSOR_OPERATION_SCALAR_TYPE)).
 * \param[in] C Pointer to the memory storing multi-mode tensor (described by `descC` as part of \ref nvpltensorCreateReduction).
 * \param[out] D Pointer to the memory storing multi-mode tensor (described by `descD` as part of \ref nvpltensorCreateReduction).
 * \param[out] workspace Scratchpad memory of size (at least) `workspaceSize` bytes; the workspace must be aligned to 256 bytes.
 * \param[in] workspaceSize Please use \ref nvpltensorEstimateWorkspaceSize() to query the required workspace.
 * \retval NVPLTENSOR_STATUS_SUCCESS The operation completed successfully.
 */
nvpltensorStatus_t nvpltensorReduce(
                 const nvpltensorHandle_t handle, const nvpltensorPlan_t plan,
                 const void* alpha, const void* A,
                 const void* beta,  const void* C,
                                          void* D,
                 void* workspace, uint64_t workspaceSize);

/**
 * \brief Sets number of threads to be use by nvplTensor
 * \param[in] numThreads Number of threads to use.
 * \retval NVPLTENSOR_STATUS_SUCCESS Number of threads set successfully.
 */
nvpltensorStatus_t nvpltensorSetNumThreads(const nvpltensorHandle_t handle, uint32_t numThreads);

/**
 * \brief Returns the description string for an error code
 * \param[in] error Error code to convert to string.
 * \retval The null-terminated error string.
 * \remarks non-blocking, no reentrant, and thread-safe
 */
const char* nvpltensorGetErrorString(const nvpltensorStatus_t error);

/**
 * \brief Returns Version number of the NVPLTENSOR library
 */
size_t nvpltensorGetVersion();

/**
 * \brief This function sets the logging callback routine.
 * \param[in] callback Pointer to a callback function. Check nvpltensorLoggerCallback_t.
 */
nvpltensorStatus_t nvpltensorLoggerSetCallback(nvpltensorLoggerCallback_t callback);

/**
 * \brief This function sets the logging output file.
 * \param[in] file An open file with write permission.
 */
nvpltensorStatus_t nvpltensorLoggerSetFile(FILE* file);

/**
 * \brief This function opens a logging output file in the given path.
 * \param[in] logFile Path to the logging output file.
 */
nvpltensorStatus_t nvpltensorLoggerOpenFile(const char* logFile);

/**
 * \brief This function sets the value of the logging level.
 * \param[in] level 
 * \parblock
 * Log level, should be one of the following:
 *   - 0.  Off
 *   - 1.  Errors
 *   - 2.  Performance Trace
 *   - 3.  Performance Hints
 *   - 4.  Heuristics Trace
 *   - 5.  API Trace
 * \endparblock
 */
nvpltensorStatus_t nvpltensorLoggerSetLevel(int32_t level);

/**
 * \brief This function sets the value of the log mask.
 * \param[in] mask
 * \parblock
 * Log mask, the bitwise OR of the following:
 *   - 0.  Off
 *   - 1.  Errors
 *   - 2.  Performance Trace
 *   - 4.  Performance Hints
 *   - 8.  Heuristics Trace
 *   - 16. API Trace
 * \endparblock
 */
nvpltensorStatus_t nvpltensorLoggerSetMask(int32_t mask);

/**
 * \brief This function disables logging for the entire run.
 */
nvpltensorStatus_t nvpltensorLoggerForceDisable();

#if defined(__cplusplus)
}
#endif /* __cplusplus */
