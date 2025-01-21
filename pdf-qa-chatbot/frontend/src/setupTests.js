// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Increase default timeout for all tests
jest.setTimeout(10000);

// Mock scrollIntoView since it's not implemented in JSDOM
window.HTMLElement.prototype.scrollIntoView = jest.fn();

// Mock fetch API
global.fetch = jest.fn();

// Mock FormData
global.FormData = class {
  append = jest.fn();
};

// Suppress console errors during tests
console.error = jest.fn();

// Reset all mocks before each test
beforeEach(() => {
  jest.clearAllMocks();
  fetch.mockClear();
});
