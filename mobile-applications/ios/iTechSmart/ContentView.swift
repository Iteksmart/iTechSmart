//
//  iTechSmart Suite v1.7.0 - iOS App
//  Next Generation AI-Native IT Operations Platform
//
//  Main view controller for the iTechSmart mobile application
//  Complete enterprise IT operations management from iOS devices
//

import SwiftUI
import LocalAuthentication
import Network
import CoreMotion

struct ContentView: View {
    @StateObject private var authManager = AuthenticationManager()
    @StateObject private var networkMonitor = NetworkMonitor()
    @StateObject private var appState = AppStateManager()
    
    @State private var selectedTab = 0
    @State private var showingBiometricAuth = false
    
    var body: some View {
        Group {
            if authManager.isAuthenticated {
                MainTabView(selectedTab: $selectedTab)
                    .environmentObject(authManager)
                    .environmentObject(networkMonitor)
                    .environmentObject(appState)
            } else {
                LoginView()
                    .environmentObject(authManager)
            }
        }
        .onAppear {
            setupApp()
        }
        .alert("Biometric Authentication", isPresented: $showingBiometricAuth) {
            Button("Cancel", role: .cancel) { }
            Button("Authenticate") {
                authManager.authenticateWithBiometrics()
            }
        } message: {
            Text("Use Face ID or Touch ID to securely access iTechSmart")
        }
    }
    
    private func setupApp() {
        // Initialize app components
        networkMonitor.startMonitoring()
        appState.initializeApp()
        
        // Request biometric authentication if available
        if authManager.canUseBiometrics {
            showingBiometricAuth = true
        }
    }
}

// MARK: - Main Tab View
struct MainTabView: View {
    @Binding var selectedTab: Int
    @EnvironmentObject var authManager: AuthenticationManager
    @EnvironmentObject var networkMonitor: NetworkMonitor
    @EnvironmentObject var appState: AppStateManager
    
    var body: some View {
        TabView(selection: $selectedTab) {
            DashboardView()
                .tabItem {
                    Image(systemName: "speedometer")
                    Text("Dashboard")
                }
                .tag(0)
            
            InfrastructureView()
                .tabItem {
                    Image(systemName: "server.rack")
                    Text("Infrastructure")
                }
                .tag(1)
            
            AIView()
                .tabItem {
                    Image(systemName: "brain")
                    Text("AI & ML")
                }
                .tag(2)
            
            AlertsView()
                .tabItem {
                    Image(systemName: "exclamationmark.triangle")
                    Text("Alerts")
                }
                .badge(appState.alertCount)
                .tag(3)
            
            SettingsView()
                .tabItem {
                    Image(systemName: "gear")
                    Text("Settings")
                }
                .tag(4)
        }
        .accentColor(.blue)
        .overlay(
            // Network status indicator
            HStack {
                Spacer()
                VStack {
                    if !networkMonitor.isConnected {
                        Image(systemName: "wifi.slash")
                            .foregroundColor(.red)
                            .padding(.trailing)
                    } else {
                        Image(systemName: "wifi")
                            .foregroundColor(.green)
                            .padding(.trailing)
                    }
                    Spacer()
                }
                .padding(.top, 50)
            }
            .allowsHitTesting(false)
        )
    }
}

// MARK: - Dashboard View
struct DashboardView: View {
    @EnvironmentObject var appState: AppStateManager
    @EnvironmentObject var networkMonitor: NetworkMonitor
    @State private var refreshing = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                LazyVStack(spacing: 16) {
                    // Status Overview Card
                    StatusOverviewCard()
                        .padding(.horizontal)
                    
                    // AI Predictions Card
                    AIPredictionsCard()
                        .padding(.horizontal)
                    
                    // Quick Actions
                    QuickActionsCard()
                        .padding(.horizontal)
                    
                    // System Health
                    SystemHealthCard()
                        .padding(.horizontal)
                    
                    // Recent Activities
                    RecentActivitiesCard()
                        .padding(.horizontal)
                }
                .padding(.vertical)
            }
            .navigationTitle("Dashboard")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: refreshData) {
                        Image(systemName: "arrow.clockwise")
                            .rotationEffect(.degrees(refreshing ? 360 : 0))
                            .animation(.easeInOut(duration: 1), value: refreshing)
                    }
                }
            }
            .refreshable {
                refreshData()
            }
        }
    }
    
    private func refreshData() {
        refreshing = true
        appState.refreshDashboardData()
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            refreshing = false
        }
    }
}

// MARK: - Status Overview Card
struct StatusOverviewCard: View {
    @EnvironmentObject var appState: AppStateManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("System Status")
                .font(.headline)
                .fontWeight(.bold)
            
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 12) {
                StatusMetric(
                    title: "Services",
                    value: "\(appState.activeServices)",
                    total: "\(appState.totalServices)",
                    color: .green
                )
                
                StatusMetric(
                    title: "AI Accuracy",
                    value: "\(Int(appState.aiAccuracy * 100))%",
                    total: "100%",
                    color: .blue
                )
                
                StatusMetric(
                    title: "Uptime",
                    value: "\(appState.uptime)%",
                    total: "100%",
                    color: .green
                )
                
                StatusMetric(
                    title: "Alerts",
                    value: "\(appState.alertCount)",
                    total: "Active",
                    color: appState.alertCount > 0 ? .red : .green
                )
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .gray.opacity(0.2), radius: 4, x: 0, y: 2)
    }
}

// MARK: - Status Metric
struct StatusMetric: View {
    let title: String
    let value: String
    let total: String
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundColor(.gray)
            
            Text(value)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(color)
            
            Text(total)
                .font(.caption2)
                .foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(8)
    }
}

// MARK: - AI Predictions Card
struct AIPredictionsCard: View {
    @EnvironmentObject var appState: AppStateManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("AI Predictions")
                    .font(.headline)
                    .fontWeight(.bold)
                
                Spacer()
                
                Image(systemName: "brain")
                    .foregroundColor(.blue)
            }
            
            if appState.predictions.isEmpty {
                Text("No active predictions")
                    .foregroundColor(.gray)
                    .padding()
            } else {
                ForEach(appState.predictions.prefix(3), id: \.id) { prediction in
                    PredictionRow(prediction: prediction)
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .gray.opacity(0.2), radius: 4, x: 0, y: 2)
    }
}

// MARK: - Prediction Row
struct PredictionRow: View {
    let prediction: AIPrediction
    
    var body: some View {
        HStack {
            VStack(alignment: .leading) {
                Text(prediction.title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Text(prediction.description)
                    .font(.caption)
                    .foregroundColor(.gray)
            }
            
            Spacer()
            
            VStack(alignment: .trailing) {
                Text("\(Int(prediction.confidence * 100))%")
                    .font(.caption)
                    .fontWeight(.bold)
                    .foregroundColor(predictionColor(prediction.confidence))
                
                Text(prediction.timeUntil)
                    .font(.caption2)
                    .foregroundColor(.gray)
            }
        }
        .padding(.vertical, 4)
    }
    
    private func predictionColor(_ confidence: Double) -> Color {
        switch confidence {
        case 0.8...1.0:
            return .red
        case 0.6..<0.8:
            return .orange
        default:
            return .green
        }
    }
}

// MARK: - Quick Actions Card
struct QuickActionsCard: View {
    @EnvironmentObject var appState: AppStateManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Quick Actions")
                .font(.headline)
                .fontWeight(.bold)
            
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 12) {
                QuickActionButton(
                    title: "Scan",
                    icon: "magnifyingglass",
                    color: .blue
                ) {
                    appState.initiateSystemScan()
                }
                
                QuickActionButton(
                    title: "Optimize",
                    icon: "speedometer",
                    color: .green
                ) {
                    appState.optimizeSystems()
                }
                
                QuickActionButton(
                    title: "Backup",
                    icon: "externaldrive",
                    color: .orange
                ) {
                    appState.initiateBackup()
                }
                
                QuickActionButton(
                    title: "Update",
                    icon: "arrow.clockwise",
                    color: .purple
                ) {
                    appState.checkForUpdates()
                }
                
                QuickActionButton(
                    title: "Security",
                    icon: "shield",
                    color: .red
                ) {
                    appState.runSecurityScan()
                }
                
                QuickActionButton(
                    title: "Reports",
                    icon: "doc.text",
                    color: .gray
                ) {
                    appState.generateReports()
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .gray.opacity(0.2), radius: 4, x: 0, y: 2)
    }
}

// MARK: - Quick Action Button
struct QuickActionButton: View {
    let title: String
    let icon: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                
                Text(title)
                    .font(.caption)
                    .foregroundColor(.primary)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(Color(.secondarySystemBackground))
            .cornerRadius(8)
        }
    }
}

// MARK: - System Health Card
struct SystemHealthCard: View {
    @EnvironmentObject var appState: AppStateManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("System Health")
                .font(.headline)
                .fontWeight(.bold)
            
            HStack {
                CircularProgressView(
                    progress: appState.systemHealth,
                    color: healthColor(appState.systemHealth)
                )
                .frame(width: 60, height: 60)
                
                VStack(alignment: .leading) {
                    Text("Overall Health")
                        .font(.subheadline)
                        .fontWeight(.medium)
                    
                    Text("\(Int(appState.systemHealth * 100))%")
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(healthColor(appState.systemHealth))
                }
                
                Spacer()
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .gray.opacity(0.2), radius: 4, x: 0, y: 2)
    }
    
    private func healthColor(_ health: Double) -> Color {
        switch health {
        case 0.8...1.0:
            return .green
        case 0.6..<0.8:
            return .orange
        default:
            return .red
        }
    }
}

// MARK: - Circular Progress View
struct CircularProgressView: View {
    let progress: Double
    let color: Color
    
    var body: some View {
        ZStack {
            Circle()
                .stroke(Color(.systemGray5), lineWidth: 4)
            
            Circle()
                .trim(from: 0, to: progress)
                .stroke(color, style: StrokeStyle(lineWidth: 4, lineCap: .round))
                .rotationEffect(.degrees(-90))
                .animation(.easeInOut(duration: 1), value: progress)
        }
    }
}

// MARK: - Recent Activities Card
struct RecentActivitiesCard: View {
    @EnvironmentObject var appState: AppStateManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Recent Activities")
                .font(.headline)
                .fontWeight(.bold)
            
            if appState.recentActivities.isEmpty {
                Text("No recent activities")
                    .foregroundColor(.gray)
                    .padding()
            } else {
                ForEach(appState.recentActivities.prefix(3), id: \.id) { activity in
                    ActivityRow(activity: activity)
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .gray.opacity(0.2), radius: 4, x: 0, y: 2)
    }
}

// MARK: - Activity Row
struct ActivityRow: View {
    let activity: RecentActivity
    
    var body: some View {
        HStack {
            Image(systemName: activity.icon)
                .foregroundColor(activity.color)
                .frame(width: 20)
            
            VStack(alignment: .leading) {
                Text(activity.title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Text(activity.timestamp)
                    .font(.caption)
                    .foregroundColor(.gray)
            }
            
            Spacer()
        }
        .padding(.vertical, 2)
    }
}

// MARK: - Preview
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .environmentObject(AuthenticationManager())
            .environmentObject(NetworkMonitor())
            .environmentObject(AppStateManager())
    }
}