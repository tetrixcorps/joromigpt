// /src/frontend/tests/unit/components/common/LanguageSelector.test.jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import LanguageSelector from '../../../../components/common/LanguageSelector';
import { useLanguage } from '../../../../context/LanguageContext';

// Mock the useLanguage hook
jest.mock('../../../../context/LanguageContext', () => ({
  useLanguage: jest.fn(),
  SUPPORTED_LANGUAGES: [
    { code: 'en-US', name: 'English (US)' },
    { code: 'fr-FR', name: 'French' },
    { code: 'sw-KE', name: 'Swahili' }
  ]
}));

describe('LanguageSelector', () => {
  const mockSetLanguage = jest.fn();

  beforeEach(() => {
    useLanguage.mockReturnValue({
      language: 'en-US',
      setLanguage: mockSetLanguage
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders language selector with correct options', () => {
    render(<LanguageSelector />);
    
    // Check if the component renders
    const selectElement = screen.getByLabelText('Language:');
    expect(selectElement).toBeInTheDocument();
    
    // Check if it has the correct options
    expect(screen.getByText('English (US)')).toBeInTheDocument();
    expect(screen.getByText('French')).toBeInTheDocument();
    expect(screen.getByText('Swahili')).toBeInTheDocument();
  });

  test('calls setLanguage when selection changes', () => {
    render(<LanguageSelector />);
    
    // Get the select element
    const selectElement = screen.getByLabelText('Language:');
    
    // Change the selection
    fireEvent.change(selectElement, { target: { value: 'fr-FR' } });
    
    // Check if setLanguage was called with the correct value
    expect(mockSetLanguage).toHaveBeenCalledWith('fr-FR');
  });

  test('has the correct default value', () => {
    render(<LanguageSelector />);
    
    // Get the select element
    const selectElement = screen.getByLabelText('Language:');
    
    // Check if the default value is set correctly
    expect(selectElement.value).toBe('en-US');
  });
});