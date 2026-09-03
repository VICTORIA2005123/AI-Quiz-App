package com.aiquiz.app

import android.app.Application
import com.aiquiz.app.data.local.AppDatabase
import com.aiquiz.app.data.local.EncryptedPreferencesManager

class AIQuizApplication : Application() {

    lateinit var database: AppDatabase
        private set

    lateinit var encryptedPreferences: EncryptedPreferencesManager
        private set

    override fun onCreate() {
        super.onCreate()
        instance = this
        database = AppDatabase.getDatabase(this)
        encryptedPreferences = EncryptedPreferencesManager(this)
    }

    companion object {
        lateinit var instance: AIQuizApplication
            private set
    }
}
