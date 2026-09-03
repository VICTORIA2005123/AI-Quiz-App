package com.aiquiz.app.presentation.screens.create

import android.net.Uri
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.InsertDriveFile
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CreateQuizScreen(
    onNavigateBack: () -> Unit,
    onSubmitJob: (file: File, count: Int, difficulty: String, bloom: String, pii: Boolean, humanReview: Boolean) -> Unit
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    var selectedFileUri by remember { mutableStateOf<Uri?>(null) }
    var selectedFileName by remember { mutableStateOf<String?>(null) }
    var questionCount by remember { mutableStateOf(5f) }
    var difficulty by remember { mutableStateOf("medium") }
    var bloomLevel by remember { mutableStateOf("mixed") }
    var enablePiiScrubbing by remember { mutableStateOf(true) }
    var humanReviewMode by remember { mutableStateOf(false) }
    var isProcessingFile by remember { mutableStateOf(false) }

    val supportedMimeTypes = arrayOf(
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "text/plain",
        "text/markdown",
        "text/csv",
        "text/html",
        "image/*",
        "*/*"
    )

    val filePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocument()
    ) { uri: Uri? ->
        if (uri != null) {
            try {
                selectedFileUri = uri
                var resolvedName: String? = null
                try {
                    val cursor = context.contentResolver.query(uri, null, null, null, null)
                    cursor?.use {
                        if (it.moveToFirst()) {
                            val nameIndex = it.getColumnIndex(android.provider.OpenableColumns.DISPLAY_NAME)
                            if (nameIndex != -1) {
                                resolvedName = it.getString(nameIndex)
                            }
                        }
                    }
                } catch (_: Exception) { }

                selectedFileName = resolvedName ?: "document_${System.currentTimeMillis()}"
            } catch (e: Exception) {
                Toast.makeText(context, "Could not open file: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Generate Grounded Quiz", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(20.dp)
        ) {
            // Document Selection Area
            Card(
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                ),
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable {
                        try {
                            filePickerLauncher.launch(supportedMimeTypes)
                        } catch (e: Exception) {
                            Toast.makeText(context, "Error launching file picker: ${e.message}", Toast.LENGTH_SHORT).show()
                        }
                    }
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Icon(
                        imageVector = if (selectedFileUri != null) Icons.AutoMirrored.Filled.InsertDriveFile else Icons.Default.CloudUpload,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(48.dp)
                    )
                    Text(
                        text = selectedFileName ?: "Select Document (PDF, DOCX, PPTX, XLSX, TXT, MD, Images)",
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 15.sp
                    )
                    Text(
                        text = if (selectedFileUri != null) "Tap to change file" else "Supports up to 25 MB",
                        fontSize = 13.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
                    )
                }
            }

            // Question Count Slider
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Question Count", fontWeight = FontWeight.Bold)
                        Text("${questionCount.toInt()} questions", color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
                    }
                    Slider(
                        value = questionCount,
                        onValueChange = { questionCount = it },
                        valueRange = 1f..25f,
                        steps = 23
                    )
                }
            }

            // Difficulty Chips
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Target Difficulty", fontWeight = FontWeight.Bold)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    listOf("easy", "medium", "hard", "adaptive").forEach { level ->
                        FilterChip(
                            selected = difficulty == level,
                            onClick = { difficulty = level },
                            label = { Text(level.replaceFirstChar { it.uppercase() }) }
                        )
                    }
                }
            }

            // Bloom's Taxonomy Chips
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Bloom's Taxonomy Level", fontWeight = FontWeight.Bold)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    listOf("remember", "understand", "apply", "mixed").forEach { level ->
                        FilterChip(
                            selected = bloomLevel == level,
                            onClick = { bloomLevel = level },
                            label = { Text(level.replaceFirstChar { it.uppercase() }) }
                        )
                    }
                }
            }

            // Privacy & PII Toggle
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Educational PII Redaction", fontWeight = FontWeight.Bold)
                        Text(
                            "Redacts personal emails, phones, and secrets while preserving academic and scientific terms.",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                        )
                    }
                    Switch(
                        checked = enablePiiScrubbing,
                        onCheckedChange = { enablePiiScrubbing = it }
                    )
                }
            }

            // Human Review Mode Toggle
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Generate & Review Mode", fontWeight = FontWeight.Bold)
                        Text(
                            "Inspect questions, correct answers, and source citations before starting the quiz.",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                        )
                    }
                    Switch(
                        checked = humanReviewMode,
                        onCheckedChange = { humanReviewMode = it }
                    )
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            // Submit Button
            Button(
                onClick = {
                    val uri = selectedFileUri
                    if (uri != null && !isProcessingFile) {
                        isProcessingFile = true
                        coroutineScope.launch {
                            try {
                                val tempFile = withContext(Dispatchers.IO) {
                                    val safeFileName = selectedFileName ?: "upload.bin"
                                    val destination = File(context.cacheDir, safeFileName)
                                    context.contentResolver.openInputStream(uri)?.use { input ->
                                        FileOutputStream(destination).use { output ->
                                            input.copyTo(output)
                                        }
                                    } ?: throw IllegalStateException("Unable to read selected file stream.")
                                    destination
                                }
                                onSubmitJob(
                                    tempFile,
                                    questionCount.toInt(),
                                    difficulty,
                                    bloomLevel,
                                    enablePiiScrubbing,
                                    humanReviewMode
                                )
                            } catch (e: Exception) {
                                Toast.makeText(
                                    context,
                                    "Error preparing file: ${e.localizedMessage ?: "Unknown error"}",
                                    Toast.LENGTH_LONG
                                ).show()
                            } finally {
                                isProcessingFile = false
                            }
                        }
                    }
                },
                enabled = selectedFileUri != null && !isProcessingFile,
                modifier = Modifier.fillMaxWidth().height(54.dp),
                shape = RoundedCornerShape(16.dp)
            ) {
                if (isProcessingFile) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = MaterialTheme.colorScheme.onPrimary,
                        strokeWidth = 2.dp
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Preparing Document...", fontSize = 16.sp, fontWeight = FontWeight.Bold)
                } else {
                    Icon(Icons.Default.AutoAwesome, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = if (humanReviewMode) "Generate & Review" else "Generate Grounded Quiz",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }
    }
}
