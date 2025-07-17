import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import Toons from '../../app/routes/toons';
import { ToonService, MemberService } from '../../app/api';
import type { Toon, Member } from '../../app/api/types';

// Mock the API services
vi.mock('../../app/api', () => ({
  ToonService: {
    getToons: vi.fn(),
    createToon: vi.fn(),
    updateToon: vi.fn(),
    deleteToon: vi.fn(),
  },
  MemberService: {
    getMembers: vi.fn(),
  },
}));

// Mock data
const mockMembers: Member[] = [
  { id: 1, name: 'Test Member 1', guild_id: 1, created_at: '2024-01-01T00:00:00', updated_at: '2024-01-01T00:00:00' },
  { id: 2, name: 'Test Member 2', guild_id: 1, created_at: '2024-01-01T00:00:00', updated_at: '2024-01-01T00:00:00' },
];

const mockToons: Toon[] = [
  {
    id: 1,
    username: 'MageToon',
    class: 'Mage',
    role: 'DPS',
    is_main: true,
    member_id: 1,
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-01T00:00:00',
  },
  {
    id: 2,
    username: 'TankToon',
    class: 'Warrior',
    role: 'Tank',
    is_main: false,
    member_id: 1,
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-01T00:00:00',
  },
  {
    id: 3,
    username: 'HealerToon',
    class: 'Priest',
    role: 'Healer',
    is_main: true,
    member_id: 2,
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-01T00:00:00',
  },
];

const renderToons = () => {
  return render(
    <MemoryRouter>
      <Toons />
    </MemoryRouter>
  );
};

describe('Toons', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Default mock implementations
    (ToonService.getToons as any).mockResolvedValue(mockToons);
    (MemberService.getMembers as any).mockResolvedValue(mockMembers);
    (ToonService.createToon as any).mockResolvedValue(mockToons[0]);
    (ToonService.updateToon as any).mockResolvedValue(mockToons[0]);
    (ToonService.deleteToon as any).mockResolvedValue(undefined);
  });

  describe('Initial Load', () => {
    it('renders toons page with correct title', async () => {
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('Toons')).toBeInTheDocument();
        expect(screen.getByText('Manage character profiles and their assignments')).toBeInTheDocument();
      });
    });

    it('loads and displays toons', async () => {
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('MageToon')).toBeInTheDocument();
        expect(screen.getByText('TankToon')).toBeInTheDocument();
        expect(screen.getByText('HealerToon')).toBeInTheDocument();
      });
    });

    it('shows loading state initially', () => {
      renderToons();
      
      expect(screen.getByText('Loading toons...')).toBeInTheDocument();
    });

    it('displays error when loading fails', async () => {
      (ToonService.getToons as any).mockRejectedValue(new Error('Failed to load'));
      
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('Failed to load toons')).toBeInTheDocument();
      });
    });
  });

  describe('Navigation', () => {
    it('has breadcrumb navigation', async () => {
      renderToons();
      
      await waitFor(() => {
        // Use getAllByText to allow for multiple Dashboard elements
        expect(screen.getAllByText('Dashboard').length).toBeGreaterThan(0);
        expect(screen.getAllByText('Toons').length).toBeGreaterThan(0);
      });
    });

    it('has dashboard link in header', async () => {
      renderToons();
      
      await waitFor(() => {
        // Use getAllByText to allow for multiple Dashboard elements
        const dashboardLinks = screen.getAllByText('Dashboard');
        expect(dashboardLinks.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Search and Filtering', () => {
    it('filters toons by search term', async () => {
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('MageToon')).toBeInTheDocument();
        expect(screen.getByText('TankToon')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText('Search by name, class, or role...');
      fireEvent.change(searchInput, { target: { value: 'Mage' } });

      await waitFor(() => {
        expect(screen.getByText('MageToon')).toBeInTheDocument();
        expect(screen.queryByText('TankToon')).not.toBeInTheDocument();
        expect(screen.queryByText('HealerToon')).not.toBeInTheDocument();
      });
    });

    it('filters toons by member', async () => {
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('MageToon')).toBeInTheDocument();
        expect(screen.getByText('TankToon')).toBeInTheDocument();
        expect(screen.getByText('HealerToon')).toBeInTheDocument();
      });

      const memberSelect = screen.getByLabelText('Filter by Member');
      fireEvent.change(memberSelect, { target: { value: '2' } });

      await waitFor(() => {
        expect(screen.queryByText('MageToon')).not.toBeInTheDocument();
        expect(screen.queryByText('TankToon')).not.toBeInTheDocument();
        expect(screen.getByText('HealerToon')).toBeInTheDocument();
      });
    });

    it('clears filters when clear button is clicked', async () => {
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('MageToon')).toBeInTheDocument();
        expect(screen.getByText('TankToon')).toBeInTheDocument();
        expect(screen.getByText('HealerToon')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText('Search by name, class, or role...');
      fireEvent.change(searchInput, { target: { value: 'Mage' } });

      await waitFor(() => {
        expect(screen.getByText('MageToon')).toBeInTheDocument();
        expect(screen.queryByText('TankToon')).not.toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Clear Filters'));

      await waitFor(() => {
        expect(screen.getByText('MageToon')).toBeInTheDocument();
        expect(screen.getByText('TankToon')).toBeInTheDocument();
        expect(screen.getByText('HealerToon')).toBeInTheDocument();
      });
    });

    it('shows correct count of filtered results', async () => {
      renderToons();
      
      await waitFor(() => {
        // Use getAllByText to handle multiple elements with the same text
        expect(screen.getAllByText((content, node) => !!node && !!node.textContent && node.textContent.replace(/\s+/g, ' ').includes('3 of 3 toon')).length).toBeGreaterThan(0);
      });

      const searchInput = screen.getByPlaceholderText('Search by name, class, or role...');
      fireEvent.change(searchInput, { target: { value: 'Mage' } });

      await waitFor(() => {
        // Use getAllByText to handle multiple elements with the same text
        expect(screen.getAllByText((content, node) => !!node && !!node.textContent && node.textContent.replace(/\s+/g, ' ').includes('1 of 3 toon')).length).toBeGreaterThan(0);
      });
    });
  });

  describe('Toon Display', () => {
    it('displays toon information correctly', async () => {
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('MageToon')).toBeInTheDocument();
        expect(screen.getByText('Mage')).toBeInTheDocument();
        expect(screen.getByText('DPS')).toBeInTheDocument();
        expect(screen.getByText('Test Member 1')).toBeInTheDocument();
      });
    });

    it('shows main character badge for main toons', async () => {
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('Main')).toBeInTheDocument();
      });
    });

    it('does not show main character badge for alt toons', async () => {
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('TankToon')).toBeInTheDocument();
        // TankToon is not main, so no "Main" badge should be shown
        const mainBadges = screen.getAllByText('Main');
        expect(mainBadges.length).toBe(2); // Only for MageToon and HealerToon
      });
    });
  });

  describe('Add Toon', () => {
    it('shows add form when add button is clicked', async () => {
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('Add Toon')).toBeInTheDocument();
      });

      // Use getAllByText to get all "Add Toon" elements and click the first one (the button)
      const addToonElements = screen.getAllByText('Add Toon');
      fireEvent.click(addToonElements[0]);

      await waitFor(() => {
        expect(screen.getByText('Add Toon')).toBeInTheDocument(); // Form title
        expect(screen.getByLabelText('Username')).toBeInTheDocument();
        expect(screen.getByLabelText('Class')).toBeInTheDocument();
        expect(screen.getByLabelText('Role')).toBeInTheDocument();
        expect(screen.getByLabelText('Member')).toBeInTheDocument();
      });
    });

    it('creates new toon successfully', async () => {
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('Add Toon')).toBeInTheDocument();
      });

      // Use getAllByText to get all "Add Toon" elements and click the first one (the button)
      const addToonElements = screen.getAllByText('Add Toon');
      fireEvent.click(addToonElements[0]);

      await waitFor(() => {
        expect(screen.getByLabelText('Username')).toBeInTheDocument();
      });

      // Fill form
      fireEvent.change(screen.getByLabelText('Username'), {
        target: { value: 'NewToon' },
      });
      fireEvent.change(screen.getByLabelText('Class'), {
        target: { value: 'Druid' },
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
        expect(ToonService.createToon).toHaveBeenCalledWith({
          username: 'NewToon',
          class: 'Druid',
          role: 'Healer',
          is_main: false,
          member_id: 1,
        });
      });
    });

    it('handles create error', async () => {
      (ToonService.createToon as any).mockRejectedValue({ response: { data: { detail: 'Username already exists' } } });
      
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('Add Toon')).toBeInTheDocument();
      });

      // Use getAllByText to get all "Add Toon" elements and click the first one (the button)
      const addToonElements = screen.getAllByText('Add Toon');
      fireEvent.click(addToonElements[0]);

      await waitFor(() => {
        expect(screen.getByLabelText('Username')).toBeInTheDocument();
      });

      // Fill form
      fireEvent.change(screen.getByLabelText('Username'), {
        target: { value: 'ExistingToon' },
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

      // Submit form
      const submitButton = screen.getByTestId('toon-form-submit');
      const form = submitButton.closest('form');
      fireEvent.submit(form!);

      await waitFor(() => {
        expect(screen.getByText('Username already exists')).toBeInTheDocument();
      });
    });
  });

  describe('Edit Toon', () => {
    it('shows edit form when edit button is clicked', async () => {
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('MageToon')).toBeInTheDocument();
      });

      const editButtons = screen.getAllByText('Edit');
      fireEvent.click(editButtons[0]); // Click first edit button

      await waitFor(() => {
        expect(screen.getByText('Edit Toon')).toBeInTheDocument();
        expect(screen.getByLabelText('Username')).toHaveValue('MageToon');
        expect(screen.getByLabelText('Class')).toHaveValue('Mage');
        expect(screen.getByLabelText('Role')).toHaveValue('DPS');
      });
    });

    it('updates toon successfully', async () => {
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('MageToon')).toBeInTheDocument();
      });

      const editButtons = screen.getAllByText('Edit');
      fireEvent.click(editButtons[0]);

      await waitFor(() => {
        expect(screen.getByLabelText('Username')).toBeInTheDocument();
      });

      // Update form
      fireEvent.change(screen.getByLabelText('Username'), {
        target: { value: 'UpdatedToon' },
      });
      fireEvent.change(screen.getByLabelText('Class'), {
        target: { value: 'Priest' },
      });

      // Submit form
      const submitButton = screen.getByTestId('toon-form-submit');
      const form = submitButton.closest('form');
      fireEvent.submit(form!);

      await waitFor(() => {
        expect(ToonService.updateToon).toHaveBeenCalledWith(1, {
          username: 'UpdatedToon',
          class: 'Priest',
          role: 'DPS',
          is_main: true,
          member_id: 1,
        });
      });
    });
  });

  describe('Delete Toon', () => {
    it('deletes toon when delete button is clicked and confirmed', async () => {
      // Mock window.confirm to return true
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);
      
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('MageToon')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByText('Delete');
      fireEvent.click(deleteButtons[0]); // Click first delete button

      await waitFor(() => {
        expect(ToonService.deleteToon).toHaveBeenCalledWith(1);
      });

      confirmSpy.mockRestore();
    });

    it('does not delete toon when delete is cancelled', async () => {
      // Mock window.confirm to return false
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false);
      
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('MageToon')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByText('Delete');
      fireEvent.click(deleteButtons[0]);

      expect(ToonService.deleteToon).not.toHaveBeenCalled();

      confirmSpy.mockRestore();
    });
  });

  describe('Empty State', () => {
    it('shows empty state when no toons exist', async () => {
      (ToonService.getToons as any).mockResolvedValue([]);
      
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('No toons found. Create your first toon!')).toBeInTheDocument();
        expect(screen.getByText('Add First Toon')).toBeInTheDocument();
      });
    });

    it('shows no results message when search has no matches', async () => {
      renderToons();
      
      await waitFor(() => {
        expect(screen.getByText('MageToon')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText('Search by name, class, or role...');
      fireEvent.change(searchInput, { target: { value: 'NonExistentToon' } });

      await waitFor(() => {
        expect(screen.getByText('No toons match your search criteria.')).toBeInTheDocument();
      });
    });
  });
}); 