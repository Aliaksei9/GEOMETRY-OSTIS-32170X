// src/pages/seventh-grade/UnknownProblemsChat.jsx
import React, { useState, useEffect, useRef } from 'react';
import { Typography, Input, Button, Spin } from 'antd';
import Header from '../../header';
import { useNavigate } from 'react-router';
import '../../theory-tests-problems.css';

const { Text } = Typography;

function UnknownProblemsChat() {
    const navigate = useNavigate();
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const API_URL = 'http://localhost:8000/chat'; // реальный URL API

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async () => {
        if (!inputValue.trim()) return;

        const userMsg = { role: 'user', content: inputValue.trim() };
        setMessages(prev => [...prev, userMsg]);
        setInputValue('');
        setLoading(true);

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: inputValue.trim() }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
        } catch (error) {
            console.error('Error sending message:', error);
            setMessages(prev => [...prev, { role: 'assistant', content: 'Произошла ошибка при отправке сообщения. Попробуйте позже.' }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ width: '100%', height: '100vh', display: 'flex', flexDirection: 'column', background: '#ECF7FF' }}>
            <Header showBackButton={true} />

            {/* Главный блок чата — статичный, по центру, с рамкой */}
            <div style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                maxWidth: '1100px',
                width: '95%',
                margin: '20px auto',
                background: 'white',
                border: '3px solid #6F60C1',
                borderRadius: '24px',
                overflow: 'hidden',
                boxShadow: '0 15px 40px rgba(111, 96, 193, 0.25)',
            }}>
                {/* Заголовок чата */}
                <div style={{
                    padding: '20px 30px',
                    background: '#6F60C1',
                    color: 'white',
                    textAlign: 'center',
                }}>
                    <Text strong style={{ fontSize: '32px', color: 'white' }}>
                        Решение неизвестных задач
                    </Text>
                </div>

                {/* Область сообщений — прокручивается только здесь */}
                <div style={{
                    flex: 1,
                    padding: '24px',
                    overflowY: 'auto',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '18px',
                    background: '#f8fbff',
                }}>
                    {messages.length === 0 && (
                        <div style={{ textAlign: 'center', marginTop: '60px' }}>
                            <Text style={{ fontSize: '20px', color: '#888' }}>
                                Напишите условие задачи — я помогу решить её шаг за шагом
                            </Text>
                        </div>
                    )}

                    {messages.map((msg, i) => (
                        <div
                            key={i}
                            style={{
                                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                                maxWidth: '78%',
                                background: msg.role === 'user' ? '#E3F2FD' : 'white',
                                padding: '16px 22px',
                                borderRadius: '20px',
                                border: msg.role === 'user' 
                                    ? '2px solid #1E88E5' 
                                    : '2px solid #6F60C1',
                                boxShadow: '0 4px 15px rgba(0,0,0,0.08)',
                            }}
                        >
                            <Text style={{ fontSize: '18px', color: '#1e2a6b', lineHeight: '1.6' }}>
                                {msg.content}
                            </Text>
                        </div>
                    ))}

                    {loading && (
                        <div style={{ alignSelf: 'flex-start', padding: '0 20px' }}>
                            <Spin size="large" />
                            <Text style={{ marginLeft: '12px', color: '#666' }}>Ассистент думает...</Text>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Поле ввода + кнопка */}
                <div style={{
                    padding: '20px 24px',
                    background: 'white',
                    borderTop: '2px solid #6F60C1',
                    display: 'flex',
                    gap: '14px',
                    alignItems: 'center',
                }}>
                    <Input
                        placeholder="Введите сообщение..."
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onPressEnter={sendMessage}
                        style={{
                            height: '58px',
                            fontSize: '18px',
                            borderRadius: '18px',
                            border: '2px solid #6F60C1',
                            background: '#f9fbfd',
                        }}
                        disabled={loading}
                    />
                    <Button
                        type="primary"
                        onClick={sendMessage}
                        disabled={loading || !inputValue.trim()}
                        style={{
                            height: '58px',
                            width: '130px',
                            borderRadius: '18px',
                            fontSize: '18px',
                            fontWeight: 600,
                            backgroundColor: '#6F60C1',
                            border: 'none',
                            boxShadow: '0 6px 18px rgba(111,96,193,0.4)',
                            color: 'white',
                        }}
                    >
                        Отправить
                    </Button>
                </div>
            </div>
        </div>
    );
}

export default UnknownProblemsChat;
