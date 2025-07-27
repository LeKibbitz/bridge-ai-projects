-- Create the table
create table instruments (
  id bigint primary key generated always as identity,
  name text not null
);

-- Insert some sample data into the table
insert into instruments (name)
values
  ('violin'),
  ('viola'),
  ('cello');

-- Make the data publicly readable
alter table instruments enable row level security;

create policy "public can read instruments"
on public.instruments
for select to anon
using (true);
