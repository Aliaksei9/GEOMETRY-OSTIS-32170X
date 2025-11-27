// src/pages/seventh-grade/theory/TopicWithTestButton.jsx

import React from 'react';
import { Typography, Button } from 'antd';
import { useNavigate } from 'react-router';

const { Text } = Typography;

const TopicWithTestButton = ({ title, studyPath, testTopic }) => {
    const navigate = useNavigate();

    return (
        <div className='theory-tests-problems-tabs-content'>
            {/* Заголовок — точно как в TTPTabContent */}
            <Typography.Text
                strong
                className='plain-text'
                style={{ marginLeft: '10px', fontSize: '20px' }}
            >
                {title}
            </Typography.Text>

            {/* Кнопки — в той же строке, как в тестах и задачах */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
                {/* Кнопка "Изучить" — обычная синяя */}
                <Button
                    className="button"
                    style={{ marginRight: '10px' }}
                    onClick={() => navigate(`/seven-grade-tests-theory-problems/${studyPath}`)}
                >
                    Изучить
                </Button>

                {/* Кнопка "Тест" — фиолетовая, но в том же стиле */}
                <Button
                    type="primary"
                    style={{
                        backgroundColor: '#6F60C1',
                        border: 'none',
                        color: 'white',
                        height: '40px',
                        fontSize: '18px',
                        fontWeight: '600',
                        borderRadius: '12px',
                        padding: '0 24px',
                        boxShadow: '0 4px 12px rgba(111,96,193,0.4)'
                    }}
                    onClick={() => navigate('/test/dynamic', { state: { topic: testTopic } })}
                >
                    Тест
                </Button>
            </div>
        </div>
    );
};

export default TopicWithTestButton;
