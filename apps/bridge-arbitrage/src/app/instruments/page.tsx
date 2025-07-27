import React, { useEffect, useState } from 'react'
import { supabase } from '@/utils/supabase/client'

interface Instrument {
  id: number
  name: string
}

export default function Instruments() {
  const [instruments, setInstruments] = useState<Instrument[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchInstruments = async () => {
      try {
        setLoading(true)
        const { data, error } = await supabase
          .from('instruments')
          .select()

        if (error) throw error
        setInstruments(data as Instrument[] || [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unexpected error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchInstruments()
  }, [])

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Instruments</h1>
      <div className="space-y-2">
        {instruments.map((instrument) => (
          <div key={instrument.id} className="p-2 bg-gray-100 rounded">
            {instrument.name}
          </div>
        ))}
      </div>
    </div>
  )
}
