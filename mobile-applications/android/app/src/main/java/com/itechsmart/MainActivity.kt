/*
 * iTechSmart Suite v1.7.0 - Android App
 * Next Generation AI-Native IT Operations Platform
 *
 * Main activity for the iTechSmart Android application
 * Complete enterprise IT operations management from Android devices
 */

package com.itechsmart

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.Menu
import android.view.MenuItem
import androidx.activity.compose.setContent
import androidx.appcompat.app.AppCompatActivity
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.itechsmart.ui.theme.ITechSmartTheme
import com.itechsmart.viewmodel.AuthenticationViewModel
import com.itechsmart.viewmodel.DashboardViewModel
import com.itechsmart.viewmodel.NetworkViewModel
import com.itechsmart.views.LoginScreen
import com.itechsmart.views.MainTabScreen
import com.itechsmart.utils.BiometricAuthManager
import com.itechsmart.utils.NetworkMonitor
import com.itechsmart.utils.NotificationManager

class MainActivity : AppCompatActivity() {
    
    private lateinit var authViewModel: AuthenticationViewModel
    private lateinit var dashboardViewModel: DashboardViewModel
    private lateinit var networkViewModel: NetworkViewModel
    private lateinit var biometricAuthManager: BiometricAuthManager
    private lateinit var networkMonitor: NetworkMonitor
    private lateinit var notificationManager: NotificationManager
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize ViewModels
        authViewModel = ViewModelProvider(this)[AuthenticationViewModel::class.java]
        dashboardViewModel = ViewModelProvider(this)[DashboardViewModel::class.java]
        networkViewModel = ViewModelProvider(this)[NetworkViewModel::class.java]
        
        // Initialize utilities
        biometricAuthManager = BiometricAuthManager(this)
        networkMonitor = NetworkMonitor(this)
        notificationManager = NotificationManager(this)
        
        // Start network monitoring
        networkMonitor.startMonitoring()
        
        // Setup UI
        setContent {
            ITechSmartTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val navController = rememberNavController()
                    
                    NavHost(
                        navController = navController,
                        startDestination = if (authViewModel.isAuthenticated) "main" else "login"
                    ) {
                        composable("login") {
                            LoginScreen(
                                authViewModel = authViewModel,
                                biometricAuthManager = biometricAuthManager,
                                onLoginSuccess = {
                                    navController.navigate("main") {
                                        popUpTo("login") { inclusive = true }
                                    }
                                }
                            )
                        }
                        
                        composable("main") {
                            MainTabScreen(
                                authViewModel = authViewModel,
                                dashboardViewModel = dashboardViewModel,
                                networkViewModel = networkViewModel,
                                onLogout = {
                                    navController.navigate("login") {
                                        popUpTo("main") { inclusive = true }
                                    }
                                }
                            )
                        }
                    }
                }
            }
        }
        
        // Check for biometric authentication on app start
        checkBiometricAuthentication()
        
        // Initialize background services
        initializeBackgroundServices()
    }
    
    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.main_menu, menu)
        return true
    }
    
    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.action_settings -> {
                // Navigate to settings
                true
            }
            R.id.action_notifications -> {
                // Navigate to notifications
                true
            }
            R.id.action_help -> {
                // Navigate to help
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }
    
    override fun onResume() {
        super.onResume()
        networkMonitor.startMonitoring()
    }
    
    override fun onPause() {
        super.onPause()
        networkMonitor.stopMonitoring()
    }
    
    override fun onDestroy() {
        super.onDestroy()
        networkMonitor.stopMonitoring()
    }
    
    /**
     * Check if biometric authentication is available and prompt user
     */
    private fun checkBiometricAuthentication() {
        if (biometricAuthManager.isBiometricAvailable && !authViewModel.isAuthenticated) {
            Handler(Looper.getMainLooper()).postDelayed({
                biometricAuthManager.authenticate(
                    title = "iTechSmart Authentication",
                    subtitle = "Use fingerprint or face to securely access iTechSmart",
                    description = "Enterprise-grade security for IT operations",
                    negativeButtonText = "Cancel"
                ) { success, error ->
                    if (success) {
                        authViewModel.authenticateWithBiometrics()
                    }
                }
            }, 1000) // Delay to allow UI to load
        }
    }
    
    /**
     * Initialize background services for real-time monitoring
     */
    private fun initializeBackgroundServices() {
        // Start notification service for real-time alerts
        notificationManager.createNotificationChannels()
        
        // Initialize background data synchronization
        startDataSyncService()
        
        // Initialize performance monitoring
        startPerformanceMonitoring()
    }
    
    /**
     * Start background data synchronization service
     */
    private fun startDataSyncService() {
        val serviceIntent = Intent(this, DataSyncService::class.java)
        startForegroundService(serviceIntent)
    }
    
    /**
     * Start performance monitoring service
     */
    private fun startPerformanceMonitoring() {
        val serviceIntent = Intent(this, PerformanceMonitorService::class.java)
        startService(serviceIntent)
    }
}