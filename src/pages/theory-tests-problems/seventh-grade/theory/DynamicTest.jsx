import React, { useState, useEffect } from 'react';
import { Typography, Radio, Button, Result, Spin, Alert } from 'antd';
import Header from '../../header';
import { useLocation } from 'react-router';
import '../../theory-tests-problems.css';

const { Text } = Typography;

function DynamicTest() {
    const location = useLocation();
    const topic = location.state?.topic || "Неизвестная тема";
    const [testData, setTestData] = useState(null);
    const [answers, setAnswers] = useState({});
    const [submitted, setSubmitted] = useState(false);
    const [score, setScore] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Загрузка теста с бэкенда
    useEffect(() => {
        const fetchTest = async () => {
            try {
                setLoading(true);
                setError(null);
                
                const response = await fetch('http://localhost:8001/generate-test', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        topic: topic,
                        num_questions: 10
                    })
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`HTTP ${response.status}: ${errorText}`);
                }

                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }

                setTestData(data);
            } catch (err) {
                console.error('Error fetching test:', err);
                setError(`Не удалось загрузить тест: ${err.message}`);
            } finally {
                setLoading(false);
            }
        };

        fetchTest();
    }, [topic]);

    const handleSubmit = () => {
        if (!testData) return;

        let correct = 0;
        testData.questions.forEach((q, i) => {
            if (answers[i] === q.correct_index) correct++;
        });
        setScore(correct);
        setSubmitted(true);
    };

    // Состояние загрузки
    if (loading) {
        return (
            <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Header showBackButton={true} />
                <div style={{ 
                    display: 'flex', 
                    justifyContent: 'center', 
                    alignItems: 'center', 
                    height: '50vh',
                    flexDirection: 'column',
                    gap: '20px'
                }}>
                    <Spin size="large" />
                    <Text style={{ fontSize: '18px', color: '#666' }}>
                        Генерируем уникальный тест по теме: "{topic}"
                    </Text>
                </div>
            </div>
        );
    }

    // Состояние ошибки
    if (error) {
        return (
            <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Header showBackButton={true} />
                <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
                    <Alert
                        message="Ошибка загрузки теста"
                        description={error}
                        type="error"
                        showIcon
                        action={
                            <Button 
                                size="large" 
                                onClick={() => window.location.reload()}
                                style={{ 
                                    backgroundColor: '#6F60C1', 
                                    border: 'none', 
                                    color: 'white',
                                    marginTop: '10px'
                                }}
                            >
                                Попробовать снова
                            </Button>
                        }
                    />
                    <div style={{ marginTop: '20px', padding: '20px', background: '#f5f5f5', borderRadius: '8px' }}>
                        <Text strong>Возможные причины:</Text>
                        <ul style={{ marginTop: '10px', paddingLeft: '20px' }}>
                            <li>Сервер генерации тестов не запущен</li>
                            <li>Проблема с API ключом Groq</li>
                            <li>Нет подключения к интернету</li>
                        </ul>
                    </div>
                </div>
            </div>
        );
    }

    // Результаты теста
    if (submitted) {
        return (
            <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Header showBackButton={true} />
                <div className="theory-tests-problems-main" style={{ padding: '40px' }}>
                    <Result
                        status="success"
                        title={`Тест завершён!`}
                        subTitle={`Правильных ответов: ${score} из ${testData.questions.length}`}
                        extra={[
                            <Button
                                type="primary"
                                key="back"
                                onClick={() => window.history.back()}
                                style={{ backgroundColor: '#6F60C1', border: 'none' }}
                            >
                                Вернуться к теории
                            </Button>
                        ]}
                    />
                </div>
            </div>
        );
    }

    // Основной интерфейс теста
    return (
        <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Header showBackButton={true} />

            <div className='theory-tests-problems-main' style={{ margin: '20px auto', maxWidth: '1200px'}}>
                <div className='theory-tests-problems-header' style={{ borderBottom: '2px solid #6F60C1', paddingBottom: '10px' }}>
                    <Text strong style={{ fontSize: '36px', color: '#4C3D8A' }}>
                        {testData?.test_title}
                    </Text>
                    <Text style={{ fontSize: '20px', color: '#666', display: 'block', marginTop: '8px' }}>
                        Тема: {topic}
                    </Text>
                </div>

                <div style={{ marginTop: '30px' }}>
                    {testData?.questions.map((q, i) => (
                        <div key={i} style={{ 
                            marginBottom: '40px', 
                            padding: '20px', 
                            background: 'white', 
                            borderRadius: '16px', 
                            boxShadow: '0 4px 15px rgba(0,0,0,0.05)'
                        }}>
                            <Text strong style={{ fontSize: '24px', color: '#4C3D8A' }}>
                                Вопрос {i + 1}: {q.question_text}
                            </Text>
                            <Radio.Group
                                style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}
                                onChange={(e) => setAnswers({ ...answers, [i]: e.target.value })}
                                value={answers[i]}
                            >
                                {q.options.map((opt, j) => (
                                    <Radio key={j} value={j} style={{ fontSize: '18px'}}>
                                        {opt}
                                    </Radio>
                                ))}
                            </Radio.Group>
                        </div>
                    ))}
                </div>

                <div style={{ textAlign: 'center', margin: '50px 0' }}>
                    <Button
                        type="primary"
                        size="large"
                        onClick={handleSubmit}
                        style={{
                            height: '60px',
                            padding: '0 50px',
                            fontSize: '22px',
                            backgroundColor: '#6F60C1',
                            border: 'none',
                            borderRadius: '16px',
                        }}
                    >
                        Завершить тест
                    </Button>
                </div>
            </div>
        </div>
    );
}

export default DynamicTest;