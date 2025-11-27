import React from 'react';
import { Button } from 'antd';
import { useNavigate } from 'react-router';

function UnknownProblemsButton() {
    const navigate = useNavigate();

    return (
        <div
            style={{
                width: '100%',
                maxWidth: '900px',
                margin: '-10px auto 20px',
                textAlign: 'center',
            }}
        >
            <Button
                type="primary"
                size="large"
                style={{
                    height: '50px',
               	    padding: '0 20px',
                    fontSize: '25px',
                    fontWeight: 600,
                    backgroundColor: '#6F60C1',
                    border: 'none',
                    borderRadius: '18px',
                    boxShadow: '0 8px 25px rgba(111, 96, 193, 0.35)',
                    color: 'white',
                }}
                onClick={() => navigate('/unknown-problems-chat')}
            >
                Решение неизвестных задач
            </Button>
        </div>
    );
}

export default UnknownProblemsButton;



