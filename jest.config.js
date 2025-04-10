module.exports = {
  // Handle JSX and ES modules
  transform: {
    "^.+\\.(js|jsx|ts|tsx)$": "babel-jest"
  },
  // Don't transform node_modules except for ES module dependencies
  transformIgnorePatterns: [
    "/node_modules/(?!(@modelcontextprotocol|@whiskeysockets)/)"
  ],
  // Set test environment
  testEnvironment: "jsdom",
  // Setup files to run before tests
  setupFilesAfterEnv: ["<rootDir>/jest.setup.js"],
  // Mock file extensions - using inline mocks instead of files
  moduleNameMapper: {
    "\\.(css|less|scss|sass)$": "identity-obj-proxy",
    "\\.(jpg|jpeg|png|gif|webp|svg)$": "jest-transform-stub"
  }
};