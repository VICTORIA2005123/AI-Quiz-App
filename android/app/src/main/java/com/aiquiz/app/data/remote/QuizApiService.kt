package com.aiquiz.app.data.remote

import com.aiquiz.app.data.remote.dto.*
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.*

interface QuizApiService {

    @POST("auth/token")
    suspend fun login(
        @Body loginPayload: Map<String, String>
    ): Response<TokenResponseDto>

    @POST("auth/register")
    suspend fun register(
        @Body registerPayload: Map<String, String>
    ): Response<Map<String, String>>

    @GET("auth/quota")
    suspend fun getQuota(): Response<QuotaResponseDto>

    @Multipart
    @POST("jobs")
    suspend fun submitDocument(
        @Part file: MultipartBody.Part,
        @Part("question_count") questionCount: RequestBody,
        @Part("difficulty") difficulty: RequestBody,
        @Part("bloom_level") bloomLevel: RequestBody,
        @Part("enable_pii_scrubbing") enablePiiScrubbing: RequestBody,
        @Part("strict_grounding") strictGrounding: RequestBody
    ): Response<JobStatusDto>

    @GET("jobs/{job_id}")
    suspend fun getJobStatus(
        @Path("job_id") jobId: String
    ): Response<JobStatusDto>

    @POST("jobs/{job_id}/cancel")
    suspend fun cancelJob(
        @Path("job_id") jobId: String
    ): Response<Map<String, String>>

    @GET("quizzes")
    suspend fun listQuizzes(): Response<List<QuizDto>>

    @GET("quizzes/{quiz_id}")
    suspend fun getQuizDetail(
        @Path("quiz_id") quizId: String
    ): Response<QuizDto>
}
