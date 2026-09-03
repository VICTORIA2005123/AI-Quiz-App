package com.aiquiz.app.data.repository

import com.aiquiz.app.data.local.dao.QuizDao
import com.aiquiz.app.data.local.entity.QuizEntity
import com.aiquiz.app.data.local.entity.QuestionEntity
import com.aiquiz.app.data.remote.QuizApiService
import com.aiquiz.app.data.remote.dto.QuizDto
import com.aiquiz.app.domain.model.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File

class QuizRepositoryImpl(
    private val apiService: QuizApiService,
    private val quizDao: QuizDao
) {

    fun getLocalQuizzes(): Flow<List<Quiz>> {
        return quizDao.getAllQuizzesWithQuestions().map { list ->
            list.map { item ->
                Quiz(
                    quizId = item.quiz.id,
                    title = item.quiz.title,
                    documentName = item.quiz.documentName,
                    difficulty = item.quiz.difficulty,
                    bloomLevel = item.quiz.bloomLevel,
                    questionCount = item.quiz.questionCount,
                    questions = item.questions.map { q ->
                        val optionsList: List<String> = try {
                            Json.decodeFromString(q.optionsJson)
                        } catch (e: Exception) {
                            listOf()
                        }
                        Question(
                            questionId = q.id,
                            type = q.questionType,
                            question = q.questionText,
                            options = optionsList,
                            correctAnswer = q.correctAnswer,
                            explanation = q.explanation,
                            difficulty = q.difficulty,
                            bloomLevel = q.bloomLevel,
                            source = Citation(
                                chunkId = q.sourceChunkId,
                                citation = q.citationQuote,
                                evidenceVerified = q.evidenceVerified,
                                confidenceScore = q.confidenceScore
                            )
                        )
                    },
                    createdAt = ""
                )
            }
        }
    }

    suspend fun submitDocumentJob(
        file: File,
        questionCount: Int,
        difficulty: String,
        bloomLevel: String,
        enablePiiScrubbing: Boolean,
        strictGrounding: Boolean
    ): Result<JobProgress> {
        return try {
            val requestFile = file.asRequestBody("multipart/form-data".toMediaTypeOrNull())
            val body = MultipartBody.Part.createFormData("file", file.name, requestFile)

            val countBody = questionCount.toString().toRequestBody("text/plain".toMediaTypeOrNull())
            val diffBody = difficulty.toRequestBody("text/plain".toMediaTypeOrNull())
            val bloomBody = bloomLevel.toRequestBody("text/plain".toMediaTypeOrNull())
            val piiBody = enablePiiScrubbing.toString().toRequestBody("text/plain".toMediaTypeOrNull())
            val groundBody = strictGrounding.toString().toRequestBody("text/plain".toMediaTypeOrNull())

            val response = apiService.submitDocument(body, countBody, diffBody, bloomBody, piiBody, groundBody)
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!
                Result.success(
                    JobProgress(
                        jobId = dto.jobId,
                        status = dto.status,
                        currentStep = dto.currentStep,
                        progressPercentage = dto.progressPercentage
                    )
                )
            } else {
                Result.failure(Exception("Submission failed: ${response.errorBody()?.string()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun pollJobStatus(jobId: String): Result<JobProgress> {
        return try {
            val response = apiService.getJobStatus(jobId)
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!
                var domainQuiz: Quiz? = null

                if (dto.quiz != null) {
                    domainQuiz = mapDtoToQuiz(dto.quiz)
                    // Persist to Room for offline study
                    saveQuizToLocalDb(domainQuiz)
                }

                Result.success(
                    JobProgress(
                        jobId = dto.jobId,
                        status = dto.status,
                        currentStep = dto.currentStep,
                        progressPercentage = dto.progressPercentage,
                        errorMessage = dto.errorMessage,
                        quiz = domainQuiz
                    )
                )
            } else {
                Result.failure(Exception("Poll failed: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun cancelJob(jobId: String): Result<Boolean> {
        return try {
            val response = apiService.cancelJob(jobId)
            Result.success(response.isSuccessful)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private suspend fun saveQuizToLocalDb(quiz: Quiz) {
        val quizEntity = QuizEntity(
            id = quiz.quizId,
            title = quiz.title,
            documentName = quiz.documentName,
            difficulty = quiz.difficulty,
            bloomLevel = quiz.bloomLevel,
            questionCount = quiz.questionCount
        )

        val questionEntities = quiz.questions.map { q ->
            QuestionEntity(
                id = q.questionId,
                quizId = quiz.quizId,
                questionType = q.type,
                questionText = q.question,
                optionsJson = Json.encodeToString(q.options),
                correctAnswer = q.correctAnswer,
                explanation = q.explanation,
                difficulty = q.difficulty,
                bloomLevel = q.bloomLevel,
                sourceChunkId = q.source.chunkId,
                citationQuote = q.source.citation,
                evidenceVerified = q.source.evidenceVerified,
                confidenceScore = q.source.confidenceScore
            )
        }

        quizDao.insertFullQuiz(quizEntity, questionEntities)
    }

    private fun mapDtoToQuiz(dto: QuizDto): Quiz {
        return Quiz(
            quizId = dto.quizId,
            title = dto.title,
            documentName = dto.documentName,
            difficulty = dto.difficulty,
            bloomLevel = dto.bloomLevel,
            questionCount = dto.questionCount,
            questions = dto.questions.map { q ->
                Question(
                    questionId = q.questionId,
                    type = q.type,
                    question = q.question,
                    options = q.options,
                    correctAnswer = q.correctAnswer,
                    explanation = q.explanation,
                    difficulty = q.difficulty,
                    bloomLevel = q.bloomLevel,
                    source = Citation(
                        chunkId = q.source.chunkId,
                        citation = q.source.citation,
                        evidenceVerified = q.source.evidenceVerified,
                        confidenceScore = q.source.confidenceScore
                    )
                )
            },
            createdAt = dto.createdAt
        )
    }
}
