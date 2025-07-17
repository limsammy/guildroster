import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { ToonForm } from '../../app/components/ui/ToonForm';
import type { Toon, Member } from '../../app/api/types';

// Mock data
const mockMembers: Member[] = [
  { id: 1, display_name: 'Test Member 1', guild_id: 1, created_at: '2024-01-01T00:00:00', updated_at: '2024-01-01T00:00:00' },
  { id: 2, display_name: 'Test Member 2', guild_id: 1, created_at: '2024-01-01T00:00:00', updated_at: '2024-01-01T00:00:00' },
];

const mockToon: Toon = {
  id: 1,
  username: 'TestToon',
  class: 'Mage',
  role: 'DPS',
  is_main: true,
  member_id: 1,
  created_at: '2024-01-01T00:00:00',
  updated_at: '2024-01-01T00:00:00',
};

const renderToonForm = (props = {}) => {
  const defaultProps = {
    mode: 'add' as const,
    members: mockMembers,
    onSubmit: vi.fn(),
    onCancel: vi.fn(),
    ...props,
  };
  return render(
    <MemoryRouter>
      <ToonForm {...defaultProps} />
    </MemoryRouter>
  );
};

describe('ToonForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  describe('Add Mode', () => {
    it('renders add form with correct title', () => {
      renderToonForm();
      expect(screen.getByRole('heading', { name: 'Add Toon' })).toBeInTheDocument();
    });

    it('renders all form fields', () => {
      renderToonForm();
      
      expect(screen.getByLabelText('Username')).toBeInTheDocument();
      expect(screen.getByLabelText('Class')).toBeInTheDocument();
      expect(screen.getByLabelText('Role')).toBeInTheDocument();
      expect(screen.getByLabelText('Member')).toBeInTheDocument();
      expect(screen.getByText('Main character')).toBeInTheDocument();
    });

    it('populates member dropdown with provided members', () => {
      renderToonForm();
      
      expect(screen.getByText('Test Member 1')).toBeInTheDocument();
      expect(screen.getByText('Test Member 2')).toBeInTheDocument();
    });

    it('populates class dropdown with WoW classes', () => {
      renderToonForm();
      
      const classSelect = screen.getByLabelText('Class');
      fireEvent.click(classSelect);
      
      expect(screen.getByText('Death Knight')).toBeInTheDocument();
      expect(screen.getByText('Warrior')).toBeInTheDocument();
      expect(screen.getByText('Druid')).toBeInTheDocument();
      expect(screen.getByText('Paladin')).toBeInTheDocument();
      expect(screen.getByText('Monk')).toBeInTheDocument();
      expect(screen.getByText('Rogue')).toBeInTheDocument();
      expect(screen.getByText('Hunter')).toBeInTheDocument();
      expect(screen.getByText('Mage')).toBeInTheDocument();
      expect(screen.getByText('Warlock')).toBeInTheDocument();
      expect(screen.getByText('Priest')).toBeInTheDocument();
      expect(screen.getByText('Shaman')).toBeInTheDocument();
    });

    it('populates role dropdown with WoW roles', () => {
      renderToonForm();
      
      const roleSelect = screen.getByLabelText('Role');
      fireEvent.click(roleSelect);
      
      expect(screen.getByText('DPS')).toBeInTheDocument();
      expect(screen.getByText('Healer')).toBeInTheDocument();
      expect(screen.getByText('Tank')).toBeInTheDocument();
    });

    it('submits form with valid data', async () => {
      const onSubmit = vi.fn();
      renderToonForm({ onSubmit });

      // Fill form
      fireEvent.change(screen.getByLabelText('Username'), {
        target: { value: 'NewToon' },
      });
      fireEvent.change(screen.getByLabelText('Class'), {
        target: { value: 'Priest' },
      });
      fireEvent.change(screen.getByLabelText('Role'), {
        target: { value: 'Healer' },
      });
      fireEvent.change(screen.getByLabelText('Member'), {
        target: { value: '1' },
      });

      // Submit form
      const submitButton = screen.getByTestId('toon-form-submit');
      const form = submitButton.closest('form');
      fireEvent.submit(form!);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith({
          username: 'NewToon',
          class: 'Priest',
          role: 'Healer',
          is_main: false,
          member_id: 1,
        });
      });
    });

    it('trims whitespace from username', async () => {
      const onSubmit = vi.fn();
      renderToonForm({ onSubmit });

      // Fill form with whitespace
      fireEvent.change(screen.getByLabelText('Username'), {
        target: { value: '  NewToon  ' },
      });
      fireEvent.change(screen.getByLabelText('Class'), {
        target: { value: 'Druid' },
      });
      fireEvent.change(screen.getByLabelText('Role'), {
        target: { value: 'Tank' },
      });
      fireEvent.change(screen.getByLabelText('Member'), {
        target: { value: '1' },
      });

      // Submit form
      const submitButton = screen.getByTestId('toon-form-submit');
      const form = submitButton.closest('form');
      fireEvent.submit(form!);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith({
          username: 'NewToon',
          class: 'Druid',
          role: 'Tank',
          is_main: false,
          member_id: 1,
        });
      });
    });

    it('submits form with main character checked', async () => {
      const onSubmit = vi.fn();
      renderToonForm({ onSubmit });

      // Fill form
      fireEvent.change(screen.getByLabelText('Username'), {
        target: { value: 'MainToon' },
      });
      fireEvent.change(screen.getByLabelText('Class'), {
        target: { value: 'Warrior' },
      });
      fireEvent.change(screen.getByLabelText('Role'), {
        target: { value: 'Tank' },
      });
      fireEvent.change(screen.getByLabelText('Member'), {
        target: { value: '1' },
      });

      // Check main character
      fireEvent.click(screen.getByText('Main character'));

      // Submit form
      const submitButton = screen.getByTestId('toon-form-submit');
      const form = submitButton.closest('form');
      fireEvent.submit(form!);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith({
          username: 'MainToon',
          class: 'Warrior',
          role: 'Tank',
          is_main: true,
          member_id: 1,
        });
      });
    });

    it('calls onCancel when cancel button is clicked', () => {
      const onCancel = vi.fn();
      renderToonForm({ onCancel });

      fireEvent.click(screen.getByText('Cancel'));
      expect(onCancel).toHaveBeenCalled();
    });

    it('disables submit button when form is invalid', () => {
      renderToonForm();
      
      const submitButton = screen.getByTestId('toon-form-submit');
      expect(submitButton).toBeDisabled();
    });

    it('enables submit button when form is valid', async () => {
      renderToonForm();

      // Fill form
      fireEvent.change(screen.getByLabelText('Username'), {
        target: { value: 'NewToon' },
      });
      fireEvent.change(screen.getByLabelText('Class'), {
        target: { value: 'Mage' },
      });
      fireEvent.change(screen.getByLabelText('Role'), {
        target: { value: 'DPS' },
      });
      fireEvent.change(screen.getByLabelText('Member'), {
        target: { value: '1' },
      });

      // Wait for button to be enabled
      await waitFor(() => {
        const submitButton = screen.getByTestId('toon-form-submit');
        expect(submitButton).not.toBeDisabled();
      });
    });
  });

  describe('Edit Mode', () => {
    it('renders edit form with correct title', () => {
      renderToonForm({ mode: 'edit' });
      expect(screen.getByText('Edit Toon')).toBeInTheDocument();
    });

    it('populates form with initial values', () => {
      renderToonForm({
        mode: 'edit',
        initialValues: mockToon,
      });

      expect(screen.getByLabelText('Username')).toHaveValue('TestToon');
      expect(screen.getByLabelText('Class')).toHaveValue('Mage');
      expect(screen.getByLabelText('Role')).toHaveValue('DPS');
      expect(screen.getByLabelText('Member')).toHaveValue('1');
      expect(screen.getByRole('checkbox')).toBeChecked();
    });

    it('submits form with updated data', async () => {
      const onSubmit = vi.fn();
      renderToonForm({
        mode: 'edit',
        initialValues: mockToon,
        onSubmit,
      });

      // Update form
      fireEvent.change(screen.getByLabelText('Username'), {
        target: { value: 'UpdatedToon' },
      });
      fireEvent.change(screen.getByLabelText('Class'), {
        target: { value: 'Druid' },
      });
      fireEvent.change(screen.getByLabelText('Role'), {
        target: { value: 'Healer' },
      });
      fireEvent.change(screen.getByLabelText('Member'), {
        target: { value: '2' },
      });

      // Submit form
      const submitButton = screen.getByTestId('toon-form-submit');
      const form = submitButton.closest('form');
      fireEvent.submit(form!);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith({
          username: 'UpdatedToon',
          class: 'Druid',
          role: 'Healer',
          is_main: true,
          member_id: 2,
        });
      });
    });
  });

  describe('Loading State', () => {
    it('shows loading text on submit button when loading', () => {
      renderToonForm({ loading: true });
      
      expect(screen.getByText('Adding...')).toBeInTheDocument();
    });

    it('shows saving text on submit button when editing and loading', () => {
      renderToonForm({ mode: 'edit', loading: true });
      
      expect(screen.getByText('Saving...')).toBeInTheDocument();
    });

    it('disables form fields when loading', () => {
      renderToonForm({ loading: true });
      
      expect(screen.getByLabelText('Username')).toBeDisabled();
      expect(screen.getByLabelText('Class')).toBeDisabled();
      expect(screen.getByLabelText('Role')).toBeDisabled();
      expect(screen.getByLabelText('Member')).toBeDisabled();
      expect(screen.getByText('Cancel')).toBeDisabled();
    });
  });

  describe('Error Handling', () => {
    it('displays error message when provided', () => {
      const errorMessage = 'Failed to create toon';
      renderToonForm({ error: errorMessage });
      
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });

    it('does not display error message when not provided', () => {
      renderToonForm();
      
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('shows validation errors when submitting empty form', async () => {
      renderToonForm();
      
      const submitButton = screen.getByTestId('toon-form-submit');
      const form = submitButton.closest('form');
      if (!form) throw new Error('Form not found');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('Username is required')).toBeInTheDocument();
        expect(screen.getByText('Class is required')).toBeInTheDocument();
        expect(screen.getByText('Role is required')).toBeInTheDocument();
        expect(screen.getByText('Member is required')).toBeInTheDocument();
      });
    });

    it('shows username error when username is empty', async () => {
      renderToonForm();

      // Fill only other fields
      fireEvent.change(screen.getByLabelText('Class'), {
        target: { value: 'Mage' },
      });
      fireEvent.change(screen.getByLabelText('Role'), {
        target: { value: 'DPS' },
      });
      fireEvent.change(screen.getByLabelText('Member'), {
        target: { value: '1' },
      });

      // Submit form
      const submitButton = screen.getByTestId('toon-form-submit');
      const form = submitButton.closest('form');
      if (!form) throw new Error('Form not found');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('Username is required')).toBeInTheDocument();
        expect(screen.queryByText('Class is required')).not.toBeInTheDocument();
        expect(screen.queryByText('Role is required')).not.toBeInTheDocument();
        expect(screen.queryByText('Member is required')).not.toBeInTheDocument();
      });
    });

    it('shows class error when class is not selected', async () => {
      renderToonForm();

      // Fill only other fields
      fireEvent.change(screen.getByLabelText('Username'), {
        target: { value: 'TestToon' },
      });
      fireEvent.change(screen.getByLabelText('Role'), {
        target: { value: 'DPS' },
      });
      fireEvent.change(screen.getByLabelText('Member'), {
        target: { value: '1' },
      });

      // Submit form
      const submitButton = screen.getByTestId('toon-form-submit');
      const form = submitButton.closest('form');
      if (!form) throw new Error('Form not found');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('Class is required')).toBeInTheDocument();
        expect(screen.queryByText('Username is required')).not.toBeInTheDocument();
        expect(screen.queryByText('Role is required')).not.toBeInTheDocument();
        expect(screen.queryByText('Member is required')).not.toBeInTheDocument();
      });
    });

    it('shows role error when role is not selected', async () => {
      renderToonForm();

      // Fill only other fields
      fireEvent.change(screen.getByLabelText('Username'), {
        target: { value: 'TestToon' },
      });
      fireEvent.change(screen.getByLabelText('Class'), {
        target: { value: 'Mage' },
      });
      fireEvent.change(screen.getByLabelText('Member'), {
        target: { value: '1' },
      });

      // Submit form
      const submitButton = screen.getByTestId('toon-form-submit');
      const form = submitButton.closest('form');
      if (!form) throw new Error('Form not found');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('Role is required')).toBeInTheDocument();
        expect(screen.queryByText('Username is required')).not.toBeInTheDocument();
        expect(screen.queryByText('Class is required')).not.toBeInTheDocument();
        expect(screen.queryByText('Member is required')).not.toBeInTheDocument();
      });
    });

    it('shows member error when member is not selected', async () => {
      renderToonForm();

      // Fill only other fields
      fireEvent.change(screen.getByLabelText('Username'), {
        target: { value: 'TestToon' },
      });
      fireEvent.change(screen.getByLabelText('Class'), {
        target: { value: 'Mage' },
      });
      fireEvent.change(screen.getByLabelText('Role'), {
        target: { value: 'DPS' },
      });

      // Submit form
      const submitButton = screen.getByTestId('toon-form-submit');
      const form = submitButton.closest('form');
      if (!form) throw new Error('Form not found');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('Member is required')).toBeInTheDocument();
        expect(screen.queryByText('Username is required')).not.toBeInTheDocument();
        expect(screen.queryByText('Class is required')).not.toBeInTheDocument();
        expect(screen.queryByText('Role is required')).not.toBeInTheDocument();
      });
    });

    it('clears validation errors when form becomes valid', async () => {
      renderToonForm();

      // Submit empty form to show errors
      const submitButton = screen.getByTestId('toon-form-submit');
      const form = submitButton.closest('form');
      if (!form) throw new Error('Form not found');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('Username is required')).toBeInTheDocument();
        expect(screen.getByText('Class is required')).toBeInTheDocument();
        expect(screen.getByText('Role is required')).toBeInTheDocument();
        expect(screen.getByText('Member is required')).toBeInTheDocument();
      });

      // Fill form to make it valid
      fireEvent.change(screen.getByLabelText('Username'), {
        target: { value: 'TestToon' },
      });
      fireEvent.change(screen.getByLabelText('Class'), {
        target: { value: 'Mage' },
      });
      fireEvent.change(screen.getByLabelText('Role'), {
        target: { value: 'DPS' },
      });
      fireEvent.change(screen.getByLabelText('Member'), {
        target: { value: '1' },
      });

      // Errors should be cleared when form becomes valid
      expect(screen.queryByText('Username is required')).not.toBeInTheDocument();
      expect(screen.queryByText('Class is required')).not.toBeInTheDocument();
      expect(screen.queryByText('Role is required')).not.toBeInTheDocument();
      expect(screen.queryByText('Member is required')).not.toBeInTheDocument();
    });
  });
}); 