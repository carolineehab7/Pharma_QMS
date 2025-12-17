// ===================================
// API Client for Pharmaceutical QMS
// Handles all communication with backend API
// ===================================

const API_BASE_URL = "http://localhost:5000/api";

// ===================================
// Helper Functions
// ===================================

async function apiRequest(endpoint, options = {}) {
  /**
   * Generic API request handler
   * @param {string} endpoint - API endpoint (e.g., '/deviations')
   * @param {object} options - Fetch options (method, body, etc.)
   * @returns {Promise} Response data
   */
  const url = `${API_BASE_URL}${endpoint}`;

  const defaultOptions = {
    headers: {
      "Content-Type": "application/json",
    },
  };

  const config = { ...defaultOptions, ...options };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(
        error.message || `HTTP error! status: ${response.status}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error("API Request Error:", error);
    throw error;
  }
}

// ===================================
// User API
// ===================================

const UserAPI = {
  /**
   * Get all users
   */
  getAll: async () => {
    return await apiRequest("/users");
  },

  /**
   * Get user by ID
   */
  getById: async (userId) => {
    return await apiRequest(`/users/${userId}`);
  },
};

// ===================================
// Deviation API
// ===================================

const DeviationAPI = {
  /**
   * Get all deviations with optional filters
   */
  getAll: async (filters = {}) => {
    const params = new URLSearchParams(filters);
    const query = params.toString() ? `?${params.toString()}` : "";
    return await apiRequest(`/deviations${query}`);
  },

  /**
   * Get deviation by ID
   */
  getById: async (deviationId) => {
    return await apiRequest(`/deviations/${deviationId}`);
  },

  /**
   * Create new deviation
   */
  create: async (deviationData) => {
    return await apiRequest("/deviations", {
      method: "POST",
      body: JSON.stringify(deviationData),
    });
  },

  /**
   * Update deviation
   */
  update: async (deviationId, deviationData) => {
    return await apiRequest(`/deviations/${deviationId}`, {
      method: "PUT",
      body: JSON.stringify(deviationData),
    });
  },

  /**
   * Delete deviation
   */
  delete: async (deviationId) => {
    return await apiRequest(`/deviations/${deviationId}`, {
      method: "DELETE",
    });
  },

  /**
   * Get deviation statistics
   */
  getStats: async () => {
    return await apiRequest("/deviations/stats");
  },
};

// ===================================
// CAPA API
// ===================================

const CAPAAPI = {
  /**
   * Get all CAPA records
   */
  getAll: async () => {
    return await apiRequest("/capa");
  },

  /**
   * Get CAPA by ID
   */
  getById: async (capaId) => {
    return await apiRequest(`/capa/${capaId}`);
  },

  /**
   * Create new CAPA
   */
  create: async (capaData) => {
    return await apiRequest("/capa", {
      method: "POST",
      body: JSON.stringify(capaData),
    });
  },

  /**
   * Update CAPA
   */
  update: async (capaId, capaData) => {
    return await apiRequest(`/capa/${capaId}`, {
      method: "PUT",
      body: JSON.stringify(capaData),
    });
  },

  /**
   * Get CAPA records for a specific deviation
   */
  getByDeviation: async (deviationId) => {
    return await apiRequest(`/capa/by-deviation/${deviationId}`);
  },

  /**
   * Get CAPA statistics
   */
  getStats: async () => {
    return await apiRequest("/capa/stats");
  },
};

// ===================================
// Monitoring API
// ===================================

const MonitoringAPI = {
  /**
   * Get environmental monitoring data
   */
  getEnvironmental: async (location = null) => {
    const query = location ? `?location=${encodeURIComponent(location)}` : "";
    return await apiRequest(`/monitoring/environmental${query}`);
  },

  /**
   * Get process monitoring data
   */
  getProcess: async () => {
    return await apiRequest("/monitoring/process");
  },

  /**
   * Record new monitoring measurement
   */
  record: async (monitoringData) => {
    return await apiRequest("/monitoring/record", {
      method: "POST",
      body: JSON.stringify(monitoringData),
    });
  },
};

// ===================================
// Dashboard API
// ===================================

const DashboardAPI = {
  /**
   * Get key performance indicators
   */
  getKPIs: async () => {
    return await apiRequest("/dashboard/kpis");
  },

  /**
   * Get trend data
   */
  getTrends: async () => {
    return await apiRequest("/dashboard/trends");
  },

  /**
   * Get recent activity
   */
  getRecentActivity: async () => {
    return await apiRequest("/dashboard/recent-activity");
  },
};

// ===================================
// Report API
// ===================================

const ReportAPI = {
  /**
   * Get all reports
   */
  getAll: async () => {
    return await apiRequest("/reports");
  },

  /**
   * Generate new report
   */
  generate: async (reportData) => {
    return await apiRequest("/reports/generate", {
      method: "POST",
      body: JSON.stringify(reportData),
    });
  },
};

// ===================================
// Batch API
// ===================================

const BatchAPI = {
  /**
   * Get all batches
   */
  getAll: async () => {
    return await apiRequest("/batches");
  },
};

// ===================================
// Export API modules
// ===================================

// Check if API server is running
async function checkAPIConnection() {
  try {
    const response = await fetch("http://localhost:5000/");
    if (response.ok) {
      console.log("✓ API Server connected");
      return true;
    }
  } catch (error) {
    console.warn("⚠ API Server not running. Please start the backend server.");
    console.warn("Run: python backend/api.py");
    return false;
  }
}

// Auto-check connection on load
if (typeof window !== "undefined") {
  checkAPIConnection();
}
