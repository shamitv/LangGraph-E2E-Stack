import React from 'react';
import { StepInfo } from '../types';

interface StepProgressProps {
    steps: StepInfo[];
}

const StepProgress: React.FC<StepProgressProps> = ({ steps }) => {
    if (!steps || steps.length === 0) return null;

    return (
        <div className="status-progress-container" style={{ marginTop: '10px', padding: '10px', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
            <p style={{ fontWeight: 'bold', marginBottom: '8px' }}>Execution Plan:</p>
            <ul style={{ listStyleType: 'none', padding: 0, margin: 0 }}>
                {steps.map((step) => (
                    <li key={step.id} style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
                        <span style={{ marginRight: '8px', fontSize: '1.2em' }}>
                            {step.status === 'completed' && '✅'}
                            {step.status === 'running' && '🔄'}
                            {step.status === 'failed' && '❌'}
                            {step.status === 'pending' && '⚪'}
                        </span>
                        <span style={{
                            color: step.status === 'pending' ? '#888' : '#000',
                            textDecoration: step.status === 'failed' ? 'line-through' : 'none'
                        }}>
                            {step.description}
                        </span>
                        {step.details && (
                            <span style={{ marginLeft: '10px', fontSize: '0.8em', color: '#666' }}>
                                - {step.details}
                            </span>
                        )}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default StepProgress;
