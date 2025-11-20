//
//  iTechSmart Suite v1.7.0 - Authentication Manager
//  Next Generation AI-Native IT Operations Platform
//
//  Handles biometric authentication, secure token management,
//  and enterprise-grade security for mobile applications
//

import Foundation
import LocalAuthentication
import Security
import KeychainAccess

class AuthenticationManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let keychain = Keychain(service: "com.itechsmart.mobile")
    private let context = LAContext()
    
    // Authentication tokens
    private var accessToken: String?
    private var refreshToken: String?
    
    init() {
        checkExistingAuthentication()
    }
    
    // MARK: - Public Properties
    
    var canUseBiometrics: Bool {
        var error: NSError?
        return context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
    }
    
    var biometricType: LABiometricType {
        guard canUseBiometrics else { return .none }
        
        switch context.biometryType {
        case .faceID:
            return .faceID
        case .touchID:
            return .touchID
        case .opticID:
            return .opticID
        default:
            return .none
        }
    }
    
    // MARK: - Authentication Methods
    
    func authenticateWithBiometrics() {
        isLoading = true
        errorMessage = nil
        
        let reason = "Authenticate to access iTechSmart IT Operations"
        
        context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: reason) { [weak self] success, error in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                if success {
                    self?.handleSuccessfulAuthentication()
                } else if let error = error {
                    self?.handleAuthenticationError(error)
                }
            }
        }
    }
    
    func authenticateWithCredentials(username: String, password: String) async {
        isLoading = true
        errorMessage = nil
        
        do {
            // Simulate API call for authentication
            let success = await performAuthentication(username: username, password: password)
            
            if success {
                await handleSuccessfulAuthentication()
            } else {
                await MainActor.run {
                    errorMessage = "Invalid credentials"
                    isLoading = false
                }
            }
        } catch {
            await MainActor.run {
                errorMessage = "Authentication failed: \(error.localizedDescription)"
                isLoading = false
            }
        }
    }
    
    func logout() {
        clearAuthenticationTokens()
        isAuthenticated = false
        accessToken = nil
        refreshToken = nil
        
        // Clear keychain
        try? keychain.removeAll()
    }
    
    // MARK: - Token Management
    
    func getAccessToken() -> String? {
        return accessToken
    }
    
    func refreshTokens() async -> Bool {
        guard let refreshToken = refreshToken else {
            return false
        }
        
        do {
            let newTokens = await performTokenRefresh(refreshToken: refreshToken)
            
            await MainActor.run {
                self.accessToken = newTokens.accessToken
                self.refreshToken = newTokens.refreshToken
                
                // Store in keychain
                try? self.keychain.set(newTokens.accessToken, key: "access_token")
                try? self.keychain.set(newTokens.refreshToken, key: "refresh_token")
            }
            
            return true
        } catch {
            print("Token refresh failed: \(error)")
            return false
        }
    }
    
    // MARK: - Private Methods
    
    private func checkExistingAuthentication() {
        // Check if we have valid tokens stored
        if let storedToken = try? keychain.get("access_token") {
            accessToken = storedToken
            refreshToken = try? keychain.get("refresh_token")
            
            // Validate token is still valid
            validateToken()
        }
    }
    
    @MainActor
    private func handleSuccessfulAuthentication() {
        isAuthenticated = true
        isLoading = false
        errorMessage = nil
        
        // Generate and store tokens
        generateAndStoreTokens()
    }
    
    @MainActor
    private func handleAuthenticationError(_ error: Error) {
        isLoading = false
        errorMessage = "Authentication failed: \(error.localizedDescription)"
    }
    
    private func validateToken() {
        // Simulate token validation
        // In production, this would make an API call to validate the token
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            // For demo purposes, assume token is valid
            self.isAuthenticated = true
        }
    }
    
    private func generateAndStoreTokens() {
        // Generate mock tokens
        accessToken = generateJWTToken()
        refreshToken = generateRefreshToken()
        
        // Store in keychain
        try? keychain.set(accessToken!, key: "access_token")
        try? keychain.set(refreshToken!, key: "refresh_token")
    }
    
    private func clearAuthenticationTokens() {
        try? keychain.remove("access_token")
        try? keychain.remove("refresh_token")
    }
    
    // MARK: - Mock API Methods
    
    private func performAuthentication(username: String, password: String) async -> Bool {
        // Simulate network delay
        try? await Task.sleep(nanoseconds: 1_000_000_000) // 1 second
        
        // Mock authentication logic
        return username.lowercased() == "admin" && password == "password"
    }
    
    private func performTokenRefresh(refreshToken: String) async -> (accessToken: String, refreshToken: String) {
        // Simulate network delay
        try? await Task.sleep(nanoseconds: 500_000_000) // 0.5 seconds
        
        return (
            accessToken: generateJWTToken(),
            refreshToken: generateRefreshToken()
        )
    }
    
    // MARK: - Token Generation
    
    private func generateJWTToken() -> String {
        // Mock JWT token generation
        let header = """
        {"alg":"HS256","typ":"JWT"}
        """
        
        let payload = """
        {"sub":"admin","iat":\(Date().timeIntervalSince1970),"exp":\(Date().timeIntervalSince1970 + 3600),"scope":"admin"}
        """
        
        let signature = "mock_signature"
        
        return "\(header.base64Encoded()).\(payload.base64Encoded()).\(signature)"
    }
    
    private func generateRefreshToken() -> String {
        return UUID().uuidString.replacingOccurrences(of: "-", with: "")
    }
}

// MARK: - Token Response Model
struct TokenResponse {
    let accessToken: String
    let refreshToken: String
    let expiresIn: Int
}

// MARK: - Authentication State Manager
extension AuthenticationManager {
    enum AuthenticationState {
        case unauthenticated
        case authenticating
        case authenticated
        case error(String)
    }
    
    var currentState: AuthenticationState {
        if isLoading {
            return .authenticating
        } else if isAuthenticated {
            return .authenticated
        } else if let error = errorMessage {
            return .error(error)
        } else {
            return .unauthenticated
        }
    }
}

// MARK: - Security Utilities
extension AuthenticationManager {
    func isDeviceSecure() -> Bool {
        // Check if device has passcode
        return context.canEvaluatePolicy(.deviceOwnerAuthentication, error: nil)
    }
    
    func enforceSecurityPolicy() -> Bool {
        // Additional security checks
        guard isDeviceSecure() else {
            errorMessage = "Device must have a passcode for security"
            return false
        }
        
        // Check for jailbreak/root detection (simplified)
        #if !DEBUG
        if isJailbroken() {
            errorMessage = "Device is not secure for enterprise access"
            return false
        }
        #endif
        
        return true
    }
    
    private func isJailbroken() -> Bool {
        // Simplified jailbreak detection
        let paths = [
            "/Applications/Cydia.app",
            "/Library/MobileSubstrate/MobileSubstrate.dylib",
            "/bin/bash",
            "/usr/sbin/sshd",
            "/etc/apt"
        ]
        
        return paths.contains { FileManager.default.fileExists(atPath: $0) }
    }
}

// MARK: - Biometric Type Extension
extension AuthenticationManager {
    enum LABiometricType {
        case none
        case touchID
        case faceID
        case opticID
        
        var displayName: String {
            switch self {
            case .none:
                return "None"
            case .touchID:
                return "Touch ID"
            case .faceID:
                return "Face ID"
            case .opticID:
                return "Optic ID"
            }
        }
        
        var icon: String {
            switch self {
            case .none:
                return "person.crop.circle"
            case .touchID:
                return "touchid"
            case .faceID:
                return "faceid"
            case .opticID:
                return "opticid"
            }
        }
    }
}

// MARK: - String Extension for Base64
extension String {
    func base64Encoded() -> String {
        return Data(self.utf8).base64EncodedString()
    }
}