import React, { useRef } from 'react';
import { Typography, Anchor } from 'antd';
import { useNavigate } from 'react-router';
import Header from '../../pages/theory-tests-problems/header';
import ChatButton from '../../components/corner-chat/corner-chat-button';
import './help.css'; 

const { Text, Paragraph } = Typography;

const navigationMenuItems = [
    {
        key: '1',
        title: 'Общие вопросы',
        href: '#general',
        children: [
            { key: '1-1', title: 'Что такое OSTIS Geometry?', href: '#what-is' },
            { key: '1-2', title: 'Какие разделы есть?', href: '#sections' },
            { key: '1-3', title: 'Для кого платформа?', href: '#for-whom' },
        ],
    },
    {
        key: '2',
        title: 'Теория и обучение',
        href: '#theory',
        children: [
            { key: '2-1', title: 'Как устроен раздел «Теория»?', href: '#theory-how' },
            { key: '2-2', title: 'Есть ли тесты?', href: '#tests' },
        ],
    },
    {
        key: '3',
        title: 'Холст',
        href: '#canvas',
        children: [
            { key: '3-1', title: 'Как пользоваться холстом?', href: '#canvas-use' },
            { key: '3-2', title: 'Сохраняются ли чертежи?', href: '#canvas-save' },
        ],
    },
    {
        key: '4',
        title: 'Профиль и статистика',
        href: '#profile',
    },
    {
        key: '5',
        title: 'Технические вопросы',
        href: '#tech',
    },
];

function Help() {
    const navigate = useNavigate();
    const contentRef = useRef(null);

    return (
        <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', overflowX: 'hidden' }}>
            {/* Верхняя панель */}
            <Header showBackButton={true} onBack={() => navigate(-1)} />

            {/* Фиксированный левый Anchor — как в теории */}
            <div className="sidebar-navigation">
                <Anchor
                    affix={false}
                    items={navigationMenuItems}
                    getContainer={() => contentRef.current}
                    offsetTop={100}
                />
            </div>

            {/* Основной контент — как в теории */}
            <div style={{ width: '100%', display: 'flex', justifyContent: 'center', paddingTop: '20px' }}>
                <div className="theory-tests-problems-main help-main-block">
                    <div className="theory-tests-problems-header">
                        <Text strong style={{ fontSize: '40px', color: '#1E3A8A', marginLeft: '15px' }}>
                            Помощь и часто задаваемые вопросы
                        </Text>
                    </div>

                    <div ref={contentRef} className="help-content-scroll">
                        {/* 1. Общие вопросы */}
                        <div id="general">
                            <Text strong style={{ fontSize: '28px', color: '#1E3A8A', display: 'block', margin: '40px 0 20px' }}>
                                Общие вопросы
                            </Text>

                            <div id="what-is">
                                <Paragraph className="theory-paragraph">
                                    <strong>OSTIS Geometry</strong> — это интеллектуальная образовательная платформа для изучения геометрии 7–11 классов по программе Республики Беларусь.
                                    Здесь теория объясняется понятно, задачи решаются с помощью ИИ, а чертежи строятся на интерактивном холсте.
                                </Paragraph>
                            </div>

                            <div id="sections">
                                <Paragraph className="theory-paragraph">
                                    На платформе доступны разделы:<br />
                                    • <strong>Теория</strong> — подробные темы с примерами и тестами<br />
                                    • <strong>Тесты</strong> — проверка знаний<br />
                                    • <strong>Задачи</strong> — решение с построением на холсте<br />
                                    • <strong>Холст</strong> — инструмент для геометрических построений<br />
                                    • <strong>Профиль</strong> — статистика, достижения, настройки
                                </Paragraph>
                            </div>

                            <div id="for-whom">
                                <Paragraph className="theory-paragraph">
                                    Платформа создана для:<br />
                                    • Учеников 7–11 классов<br />
                                    • Учителей (как дополнение к урокам)<br />
                                    • Всех, кто хочет глубоко понять геометрию
                                </Paragraph>
                            </div>
                        </div>

                        {/* 2. Теория */}
                        <div id="theory">
                            <Text strong style={{ fontSize: '28px', color: '#1E3A8A', display: 'block', margin: '40px 0 20px' }}>
                                Теория и обучение
                            </Text>
                            <Paragraph className="theory-paragraph">
                                Каждая тема содержит:<br />
                                • Определения, теоремы, доказательства<br />
                                • Интерактивные иллюстрации<br />
                                • Краткие тесты для самопроверки<br />
                                • Возможность задать вопрос ИИ-помощнику
                            </Paragraph>
                        </div>

                        {/* 3. Холст */}
                        <div id="canvas">
                            <Text strong style={{ fontSize: '28px', color: '#1E3A8A', display: 'block', margin: '40px 0 20px' }}>
                                Холст
                            </Text>
                            <Paragraph className="theory-paragraph">
                                Холст — это полноценный геометрический редактор.<br />
                                Вы можете:<br />
                                • Строить точки, отрезки, окружности, углы<br />
                                • Измерять длины и углы<br />
                                • Подписывать объекты<br />
                                • Сохранять чертежи автоматически<br />
                                • Экспортировать в PNG
                            </Paragraph>
                        </div>

                        {/* 4. Профиль */}
                        <div id="profile">
                            <Text strong style={{ fontSize: '28px', color: '#1E3A8A', display: 'block', margin: '40px 0 20px' }}>
                                Профиль и статистика
                            </Text>
                            <Paragraph className="theory-paragraph">
                                В профиле вы видите:<br />
                                • Пройденные тесты и баллы<br />
                                • Время обучения<br />
                                • Достижения<br />
                                • Сохранённые чертежи
                            </Paragraph>
                        </div>

                        {/* 5. Технические вопросы */}
                        <div id="tech">
                            <Text strong style={{ fontSize: '28px', color: '#1E3A8A', display: 'block', margin: '40px 0 20px' }}>
                                Технические вопросы
                            </Text>
                            <Paragraph className="theory-paragraph">
                                • Платформа работает в любом современном браузере<br />
                                • Регистрация обязательна для сохранения прогресса<br />
                                • Все данные хранятся безопасно<br />
                                • Поддержка: alicebobovna@gmail.com
                            </Paragraph>
                        </div>
                    </div>
                </div>
            </div>

            <ChatButton />
        </div>
    );
}

export default Help;
