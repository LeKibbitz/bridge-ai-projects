import React, { useEffect, useState } from 'react';
import { supabase } from '../utils/supabaseClient';

const ParsingProgress = () => {
    const [progress, setProgress] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Subscribe to real-time updates
        const channel = supabase
            .channel('parsing_progress')
            .on(
                'postgres_changes',
                {
                    event: '*',
                    schema: 'public',
                    table: 'parsing_progress',
                },
                (payload) => {
                    fetchProgress();
                }
            )
            .subscribe();

        fetchProgress();

        return () => {
            supabase.removeChannel(channel);
        };
    }, []);

    const fetchProgress = async () => {
        try {
            const { data, error } = await supabase
                .from('parsing_progress')
                .select('*')
                .order('last_updated', { ascending: false })
                .limit(1);

            if (error) throw error;
            
            setProgress(data[0]);
            setError(null);
        } catch (err) {
            setError(err.message);
        }
    };

    if (error) {
        return <div className="text-red-500">Error: {error}</div>;
    }

    if (!progress) {
        return <div>Waiting for parsing progress...</div>;
    }

    return (
        <div className="p-4 bg-gray-100 rounded-lg">
            <h2 className="text-xl font-bold mb-4">Parsing Progress</h2>
            <div className="mb-4">
                <div className="text-sm text-gray-600 mb-2">Document Type:</div>
                <div className="font-medium">{progress.document_type}</div>
            </div>
            <div className="mb-4">
                <div className="text-sm text-gray-600 mb-2">Current Location:</div>
                <div className="font-medium">
                    {progress.current_section || 'N/A'} - 
                    {progress.current_chapter || 'N/A'} - 
                    {progress.current_article || 'N/A'} - 
                    {progress.current_alinea || 'N/A'} - 
                    {progress.current_sub_alinea || 'N/A'}
                </div>
            </div>
            <div className="mb-4">
                <div className="text-sm text-gray-600 mb-2">Progress:</div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div 
                        className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                        style={{ width: `${progress.progress_percentage}%` }}
                    ></div>
                </div>
                <div className="text-sm text-gray-600 mt-1">
                    {progress.progress_percentage}%
                </div>
            </div>
            <div className="mb-4">
                <div className="text-sm text-gray-600 mb-2">Status:</div>
                <div className={`font-medium ${getStatusColor(progress.status)}`}>
                    {progress.status}
                </div>
            </div>
            {progress.error_message && (
                <div className="text-red-500 mt-4">
                    Error: {progress.error_message}
                </div>
            )}
        </div>
    );
};

const getStatusColor = (status) => {
    switch (status) {
        case 'parsing':
            return 'text-blue-500';
        case 'completed':
            return 'text-green-500';
        case 'error':
            return 'text-red-500';
        default:
            return 'text-gray-500';
    }
};

export default ParsingProgress;
