import React, { useState } from 'react';
import { Typography, Radio, Button, Result } from 'antd';
import Header from '../../header';
import { useLocation } from 'react-router';
import '../../theory-tests-problems.css';

const { Text } = Typography;

// Заглушка — потом заменится на ответ от API
const MOCK_TEST = {
    test_title: "Тест: Прямая, луч, отрезок. Ломаная",
    questions: [
        {
            question_text: "Что такое луч?",
            options: [
                "Отрезок с одним концом",
                "Бесконечная линия в обе стороны",
                "Часть прямой с началом в одной точке и бесконечная в одном направлении",
                "Два отрезка, соединённых в одной точке"
            ],
            correct_index: 2
        },
        {
            question_text: "Сколько точек определяют прямую?",
            options: ["Одну", "Две", "Три", "Любое количество"],
            correct_index: 1
        },
        {
            question_text: "Ломаная линия — это:",
            options: [
                "Кривая линия",
                "Последовательность отрезков, соединённых концами",
                "Прямая с изломами",
                "Окружность"
            ],
            correct_index: 1
        },
        // ... ещё 5 вопросов — добавь сам или оставь так
    ].slice(0, 8).concat(Array(5).fill(null).map((_, i) => ({
        question_text: `Пример вопроса ${i + 4} по теме`,
        options: ["Вариант A", "Вариант B", "Вариант C", "Вариант D"],
        correct_index: 1
    })))
};

function DynamicTest() {
    const location = useLocation();
    const topic = location.state?.topic || "Неизвестная тема";
    const [answers, setAnswers] = useState({});
    const [submitted, setSubmitted] = useState(false);
    const [score, setScore] = useState(0);

    const handleSubmit = () => {
        let correct = 0;
        MOCK_TEST.questions.forEach((q, i) => {
            if (answers[i] === q.correct_index) correct++;
        });
        setScore(correct);
        setSubmitted(true);
    };

    if (submitted) {
        return (
            <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Header showBackButton={true} />
                <div className="theory-tests-problems-main" style={{ padding: '40px' }}>
                    <Result
                        status="success"
                        title={`Тест завершён!`}
                        subTitle={`Правильных ответов: ${score} из ${MOCK_TEST.questions.length}`}
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

    return (
        <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Header showBackButton={true} />

            <div className='theory-tests-problems-main' style={{ margin: '20px auto', maxWidth: '1200px' }}>
                <div className='theory-tests-problems-header' style={{ borderBottom: '2px solid #6F60C1', paddingBottom: '10px' }}>
                    <Text strong style={{ fontSize: '36px', color: '#4C3D8A' }}>
                        {MOCK_TEST.test_title}
                    </Text>
                    <Text style={{ fontSize: '20px', color: '#666', display: 'block', marginTop: '8px' }}>
                        Тема: {topic}
                    </Text>
                </div>

                <div style={{ marginTop: '30px' }}>
                    {MOCK_TEST.questions.map((q, i) => (
                        <div key={i} style={{ marginBottom: '40px', padding: '20px', background: 'white', borderRadius: '16px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)' }}>
                            <Text strong style={{ fontSize: '24px', color: '#4C3D8A' }}>
                                Вопрос {i + 1}: {q.question_text}
                            </Text>
                            <Radio.Group
                                style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}
                                onChange={(e) => setAnswers({ ...answers, [i]: e.target.value })}
                                value={answers[i]}
                            >
                                {q.options.map((opt, j) => (
                                    <Radio key={j} value={j} style={{ fontSize: '18px' }}>
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
