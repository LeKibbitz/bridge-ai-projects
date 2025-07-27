import React, { useState } from 'react';
import { supabase } from '../utils/supabaseClient';
import ParsingProgress from './ParsingProgress';

const ParsingControls = () => {
    const [selectedDocument, setSelectedDocument] = useState('');
    const [documentType, setDocumentType] = useState('code_laws');
    const [isParsing, setIsParsing] = useState(false);
    const [error, setError] = useState('');

    const handleFileChange = async (event) => {
        const file = event.target.files[0];
        if (file) {
            setSelectedDocument(file.name);
        }
    };

    const startParsing = async () => {
        if (!selectedDocument) {
            setError('Please select a document to parse');
            return;
        }

        setIsParsing(true);
        setError('');

        try {
            // First, update the parsing progress status
            await supabase
                .from('parsing_progress')
                .upsert({
                    document_type: documentType,
                    status: 'parsing',
                    current_section: null,
                    current_chapter: null,
                    current_article: null,
                    current_alinea: null,
                    current_sub_alinea: null,
                    progress_percentage: 0
                });

            // Get the path to the selected document
            const filePath = `/Users/lekibbitz/Projets/bridge-arbitrage/public/Upload/${selectedDocument}`;

            // Call the appropriate parsing function
            const { parseCodeLaws, parseRNC } = require('../scripts/parse_documents');
            
            if (documentType === 'code_laws') {
                await parseCodeLaws(filePath);
            } else {
                await parseRNC(filePath);
            }

            setIsParsing(false);
        } catch (err) {
            setError(err.message);
            setIsParsing(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto p-8">
            <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold mb-6">Document Parsing Controls</h2>

                <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Select Document Type
                    </label>
                    <select
                        value={documentType}
                        onChange={(e) => setDocumentType(e.target.value)}
                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                    >
                        <option value="code_laws">Code Laws</option>
                        <option value="rnc_articles">RNC Articles</option>
                    </select>
                </div>

                <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Select Document
                    </label>
                    <input
                        type="file"
                        onChange={handleFileChange}
                        className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        accept=".pdf,.txt"
                    />
                </div>

                <button
                    onClick={startParsing}
                    disabled={isParsing || !selectedDocument}
                    className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium ${
                        isParsing
                            ? 'bg-gray-400 text-gray-700 cursor-not-allowed'
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                >
                    {isParsing ? 'Parsing...' : 'Start Parsing'}
                </button>

                {error && (
                    <div className="mt-4 text-red-500">{error}</div>
                )}
            </div>

            <div className="mt-8">
                <ParsingProgress />
            </div>
        </div>
    );
};

export default ParsingControls;
