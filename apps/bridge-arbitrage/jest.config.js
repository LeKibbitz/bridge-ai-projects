module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/test/**/*.test.js'],
  moduleFileExtensions: ['js'],
  testPathIgnorePatterns: ['/node_modules/'],
  setupFiles: ['./test/setup.js']
};
