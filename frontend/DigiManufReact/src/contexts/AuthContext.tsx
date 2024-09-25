import React, { createContext, useState, useContext, useEffect } from 'react';

// Define the shape of the authentication context
interface AuthContextType {
    user: any;
    login: (email: string, password: string) => Promise<void>;
    logout: () => void;
    isLoading: boolean;
    error: string | null;
}

// Create the AuthContext
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// AuthProvider component to wrap the app with authentication context
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false); // Loading state for async operations
    const [error, setError] = useState<string | null>(null); // Error handling

    // Login function to handle user authentication
    const login = async (email: string, password: string) => {
        setIsLoading(true);
        setError(null);
    
        try {
            const response = await fetch('http://localhost:3001/api/auth/signin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });
    
            // Check if the login is successful based on the response status or data
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Login failed. Please check your credentials.');
            }
    
            const data = await response.json();
    
            // If login is successful, update the user state
            setUser(data.user); // Assuming the response includes user info
            console.log('Login successful:', data);
        } catch (err: any) {
            setError(err.message); // Show the error message
            console.error('Login error:', err);
        } finally {
            setIsLoading(false);
        }
    };
    

    // Logout function to handle user logout
    const logout = () => {
        setUser(null); // Clear the user state
        // You can also clear tokens or session-related data if necessary
        console.log('User logged out');
    };

    // You can add more logic to persist the user session (e.g., JWT in localStorage)
    useEffect(() => {
        // Optionally check for user session on component mount (e.g., check token in localStorage)
        const savedUser = localStorage.getItem('user');
        if (savedUser) {
            setUser(JSON.parse(savedUser));
        }
    }, []);

    useEffect(() => {
        // Optionally save user to localStorage when user state changes
        if (user) {
            localStorage.setItem('user', JSON.stringify(user));
        } else {
            localStorage.removeItem('user');
        }
    }, [user]);

    return (
        <AuthContext.Provider value={{ user, login, logout, isLoading, error }}>
            {children}
        </AuthContext.Provider>
    );
};

// Hook to use authentication context
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
