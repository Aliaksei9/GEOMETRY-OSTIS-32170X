import React from 'react';
import { Typography, Form, Radio, Checkbox, Input, Button } from 'antd';
import Header from '../../header';
import '../../theory-tests-problems.css';
import { useNavigate } from 'react-router';

const { Text } = Typography;

const question2Values = [
    {
        label: 'Ломаная, у которой отрезки не пересекаются, кроме вершин',
        value: 1,
    },
    {
        label: 'Ломаная, у которой начало совпадает с концом',
        value: 2,
    },
    {
        label: 'Ломаная, состоящая из одного отрезка',
        value: 3,
    },
];

function Test1() {
    const navigate = useNavigate();

    const handleFormFinish = (values) => {
        for (let key in values) {
            console.log(`${key} : ${values[key]}\n`);
        }
        navigate('/seven-grade-tests-theory-problems');
    };

    return (
        <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', overflowX: 'hidden' }}>
            <Header showBackButton={true} />
            <div className='theory-tests-problems-main' style={{ margin: '17px auto 40px', maxWidth: '1700px' }}>
                <div className='theory-tests-problems-header' style={{ borderBottom: '1px solid #84B7EE' }}>
                    <Text strong className='header-text' style={{ fontSize: '40px', marginLeft: '15px', color: '#4C3D8A' }}>
                        1. Прямая, луч, отрезок. Ломаная
                    </Text>
                </div>
                <Form
                    name='test-form-checkboxes'
                    layout='vertical'
                    onFinish={handleFormFinish}
                    scrollToFirstError={true}
                    style={{ width: '95%', margin: '20px auto' }}
                >
                    <div className='test-question-box'>
                        <Text className='question-text' style={{ marginLeft: '5px', fontSize: '28px', color: '#4C3D8A' }}>
                            Вопрос 1
                        </Text>
                        <Form.Item
                            label='Выберите правильный вариант ответа:'
                            name='question1'
                            rules={[{ required: true, message: 'Вопрос обязателен' }]}
                        >
                            <Radio.Group style={{ display: 'flex', flexDirection: 'column', marginLeft: '5px', marginBottom: '10px' }}>
                                <Radio value={1} className='test-question-item'>Прямая имеет начало и конец</Radio>
                                <Radio value={2} className='test-question-item'>Прямая проходит через любые две точки и бесконечна</Radio>
                                <Radio value={3} className='test-question-item'>Прямая имеет только одну конечную точку</Radio>
                            </Radio.Group>
                        </Form.Item>
                    </div>

                    <div className='test-question-box'>
                        <Text className='question-text' style={{ marginLeft: '5px', fontSize: '28px', color: '#4C3D8A' }}>
                            Вопрос 2
                        </Text>
                        <Form.Item
                            label='Выберите правильные варианты ответа:'
                            name='question2'
                            rules={[{ required: true, message: 'Вопрос обязателен' }]}
                        >
                            <Checkbox.Group
                                direction='vertical'
                                size='small'
                                style={{ display: 'flex', marginLeft: '5px', marginBottom: '10px' }}
                                options={question2Values}
                            />
                        </Form.Item>
                    </div>

                    <div className='test-question-box'>
                        <Text className='question-text' style={{ marginLeft: '5px', fontSize: '28px', color: '#4C3D8A' }}>
                            Вопрос 3
                        </Text>
                        <Form.Item
                            label='Напишите свой вариант ответа:'
                            name='question3'
                            rules={[{ required: true, message: 'Вопрос обязателен' }]}
                        >
                            <Input.TextArea
                                placeholder='Введите свой ответ'
                                className='test-question-item'
                                style={{ marginLeft: '10px' }}
                                autoSize
                            />
                        </Form.Item>
                    </div>

                    <div className='test-question-box'>
                        <Text className='question-text' style={{ marginLeft: '5px', fontSize: '28px', color: '#4C3D8A' }}>
                            Вопрос 4
                        </Text>
                        <Form.Item
                            label='Выберите правильный вариант ответа:'
                            name='question4'
                        >
                            <Radio.Group style={{ display: 'flex', flexDirection: 'column', marginLeft: '5px', marginBottom: '10px' }}>
                                <Radio value={1} className='test-question-item'>Луч имеет две конечные точки</Radio>
                                <Radio value={2} className='test-question-item'>Луч начинается в одной точке и бесконечен в одном направлении</Radio>
                                <Radio value={3} className='test-question-item'>Луч бесконечен в обе стороны</Radio>
                            </Radio.Group>
                        </Form.Item>
                    </div>

                    <div className='test-question-box'>
                        <Text className='question-text' style={{ marginLeft: '5px', fontSize: '28px', color: '#4C3D8A' }}>
                            Вопрос 5
                        </Text>
                        <Form.Item
                            label='Выберите правильные варианты ответа:'
                            name='question5'
                        >
                            <Checkbox.Group
                                direction='vertical'
                                size='small'
                                style={{ display: 'flex', marginLeft: '5px', marginBottom: '10px' }}
                                options={question2Values}
                            />
                        </Form.Item>
                    </div>

                    <div className='test-question-box'>
                        <Text className='question-text' style={{ marginLeft: '5px', fontSize: '28px', color: '#4C3D8A' }}>
                            Вопрос 6
                        </Text>
                        <Form.Item
                            label='Напишите свой вариант ответа:'
                            name='question6'
                        >
                            <Input.TextArea
                                placeholder='Введите свой ответ'
                                className='test-question-item'
                                style={{ marginLeft: '10px' }}
                                autoSize
                            />
                        </Form.Item>
                    </div>

                    <div style={{ width: '100%', display: 'flex', flexDirection: 'row-reverse' }}>
                        <Form.Item>
                            <Button type='primary' htmlType='submit' className='button' style={{ color: '#1E40AF' }}>
                                Закончить
                            </Button>
                        </Form.Item>
                    </div>
                </Form>
            </div>
        </div>
    );
}

export default Test1;
