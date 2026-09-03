package com.aiquiz.app.data.local.dao

import androidx.room.*
import com.aiquiz.app.data.local.entity.QuizEntity
import com.aiquiz.app.data.local.entity.QuestionEntity
import kotlinx.coroutines.flow.Flow

data class QuizWithQuestions(
    @Embedded val quiz: QuizEntity,
    @Relation(
        parentColumn = "id",
        entityColumn = "quizId"
    )
    val questions: List<QuestionEntity>
)

@Dao
interface QuizDao {
    @Transaction
    @Query("SELECT * FROM local_quizzes ORDER BY createdAtEpoch DESC")
    fun getAllQuizzesWithQuestions(): Flow<List<QuizWithQuestions>>

    @Transaction
    @Query("SELECT * FROM local_quizzes WHERE id = :quizId LIMIT 1")
    suspend fun getQuizById(quizId: String): QuizWithQuestions?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertQuiz(quiz: QuizEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertQuestions(questions: List<QuestionEntity>)

    @Transaction
    suspend fun insertFullQuiz(quiz: QuizEntity, questions: List<QuestionEntity>) {
        insertQuiz(quiz)
        insertQuestions(questions)
    }

    @Query("DELETE FROM local_quizzes WHERE id = :quizId")
    suspend fun deleteQuiz(quizId: String)
}
