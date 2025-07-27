import { supabase } from '../src/supabaseClient';

describe('Supabase Client', () => {
  test('should initialize properly', () => {
    expect(supabase).toBeDefined();
    expect(supabase.auth).toBeDefined();
    expect(supabase.from).toBeDefined();
  });

  test('should have correct configuration', () => {
    expect(supabase.config.apiKey).toBeDefined();
    expect(supabase.config.url).toBeDefined();
  });
});
