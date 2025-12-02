import React, { useRef } from 'react';
import { Typography, Anchor } from 'antd';
import { useNavigate } from 'react-router';
import ChatButton from '../../../../../components/corner-chat/corner-chat-button';
import Header from '../../../header';
import '../../../theory-tests-problems.css';
import pic1 from './pic1.png';
import { TheoryDTPABlock } from '../../../theory-tests-problems';

const { Text, Paragraph } = Typography;

const navigationMenuItems = [
    {
        key: 'sub1',
        title: 'I. Прямая, луч, отрезок.',
        href: '#прямая-луч-отрезок',
        children: [
            { key: '1', title: 'a. Прямая', href: '#прямая' },
            { key: '2', title: 'б. Луч', href: '#луч' },
            { key: '3', title: 'в. Отрезок', href: '#отрезок' },
        ],
    },
    { key: '4', title: 'II. Ломаная и её типы', href: '#ломаная-и-типы' },
];

function Theme1() {
    const navigate = useNavigate();
    const scrollRef = useRef(null);

    return (
        <div className="ttp-root-wrapper">
            <Header showBackButton={true} />

            {/* Боковая панель — без изменений */}
            <div
                className="sidebar-navigation"
                style={{
                    position: 'fixed',
                    left: '20px',
                    top: 'calc(7.5% + 20px)',
                    width: '280px',
                    backgroundColor: '#D6E8FF',
                    border: '2px solid #84B7EE',
                    borderRadius: '15px',
                    padding: '15px',
                    overflowY: 'auto',
                    zIndex: 10,
                    maxHeight: 'calc(100vh - 9%)',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                }}
            >
                <Anchor
                    affix={false}
                    items={navigationMenuItems}
                    getContainer={() => scrollRef.current || window}
                />
            </div>

            {/* Центральная часть — ТОЧНО как у тебя было */}
            <div style={{
                width: '100%',
                display: 'flex',
                justifyContent: 'center',
                paddingTop: '0px',
            }}>
                <div
                    className="theory-tests-problems-main"
                    style={{
                        width: '100%',
                        maxWidth: '1600px',
                        backgroundColor: '#C8E4FF',
                        border: '2px solid #6F60C1',
                        borderRadius: '15px',
                        padding: '20px',
                        boxShadow: '0 4px 20px rgba(0,0,0,0.1)',

                        /* КЛЮЧЕВЫЕ ИСПРАВЛЕНИЯ — теперь блок НЕ ВЫЛЕЗЕТ за экран */
                        height: '1330px',   // 100px ≈ высота хедера + отступы
                        maxHeight: 'calc(100vh - 100px)',
                        display: 'flex',
                        flexDirection: 'column',
                        overflow: 'hidden',              // убираем любой скролл у самого блока
                        boxSizing: 'border-box',
                    }}
                >
                    {/* Заголовок темы — фиксирован сверху */}
                    <div style={{
                        borderBottom: '1px solid #84B7EE',
                        paddingBottom: '12px',
                        marginBottom: '20px',
                        flexShrink: 0,
                        textAlign: 'center',
                    }}>
                        <Text strong style={{ fontSize: '40px', color: '#1E3A8A' }}>
                            1. Прямая, луч, отрезок. Ломаная
                        </Text>
                    </div>

                    {/* ТОЛЬКО ЭТОТ DIV СКРОЛЛИТСЯ */}
                    <div
                        ref={scrollRef}
                        className="ttp-scroll-area"
                        style={{
                            flex: 1,
                            overflowY: 'auto',
                            overflowX: 'hidden',
                            paddingRight: '80px',  
                            paddingLeft: '80px', // место под красивый скроллбар
                        }}
                    >
                        {/* ← ВЕСЬ ТВОЙ КОНТЕНТ ТЕМЫ ЗДЕСЬ → */}
                        <Text strong style={{ fontSize: '28px', color: '#1E3A8A', display: 'block', marginBottom: '20px' }}>
                            I. Прямая, луч, отрезок.
                        </Text>
                        <Paragraph id='прямая-луч-отрезок' ellipsis={{ defaultExpanded: true }} className='theory-paragraph'>
                            Прямые, лучи и отрезки являются основными геометрическими объектами, которые используются для построения более сложных фигур. Они лежат в основе многих геометрических понятий и теорем. В этом разделе мы рассмотрим их определения и основные свойства.
                        </Paragraph>
                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
                            <img src={pic1} alt='Прямая, луч, отрезок' style={{ width: '300px', height: '250px', marginRight: '10px' }} />
                            <Paragraph ellipsis={{ defaultExpanded: true }} className='theory-paragraph' style={{ width: 'calc(100% - 340px)' }}>
                                На изображении показаны примеры прямой, луча и отрезка. Прямая бесконечна и проходит через любые две точки. Луч имеет начало, но бесконечен в одном направлении. Отрезок ограничен двумя точками. Эти понятия помогают описывать положение и взаимодействие объектов в пространстве.
                            </Paragraph>
                        </div>
                        <TheoryDTPABlock definition id='прямая'>
                            Прямая — это геометрическое место точек, которое не имеет начала и конца и проходит через любые две точки. Прямая обозначается обычно двумя точками, например, AB.
                        </TheoryDTPABlock>
                        <TheoryDTPABlock theorem>
                            Через любые две точки можно провести ровно одну прямую.
                        </TheoryDTPABlock>
                        <Paragraph ellipsis={{ defaultExpanded: true }} className='theory-paragraph'>
                            Это свойство прямой является аксиомой евклидовой геометрии и используется для построения всех геометрических фигур.
                        </Paragraph>
                        <TheoryDTPABlock proof>
                            Доказательство: Если взять две точки A и B, то существует только одна прямая, проходящая через них, так как любая другая линия, проходящая через эти точки, либо совпадёт с первой, либо не будет прямой.
                        </TheoryDTPABlock>
                        <TheoryDTPABlock axiom>
                            Через любую точку, не лежащую на данной прямой, можно провести ровно одну прямую, параллельную данной.
                        </TheoryDTPABlock>
                        <TheoryDTPABlock definition id='луч'>
                            Луч — это часть прямой, которая имеет начало в одной точке и простирается бесконечно в одном направлении. Например, луч AB начинается в точке A и продолжается через точку B.
                        </TheoryDTPABlock>
                        <Paragraph ellipsis={{ defaultExpanded: true }} className='theory-paragraph'>
                            Луч используется для описания направленных объектов, таких как векторы или лучи света в физике. Важно понимать, что луч имеет только одну конечную точку.
                        </Paragraph>
                        <Paragraph ellipsis={{ defaultExpanded: true }} className='theory-paragraph'>
                            Свойства луча включают его направленность и бесконечность в одном направлении. Например, два луча, начинающихся в одной точке, могут образовывать угол.
                        </Paragraph>
                        <TheoryDTPABlock definition id='отрезок'>
                            Отрезок — это часть прямой, ограниченная двумя точками, называемыми концами отрезка. Например, отрезок AB включает точки A и B и все точки между ними.
                        </TheoryDTPABlock>
                        <Text strong className='subheader-text' style={{ fontSize: '28px', color: '#1E3A8A', marginBottom: '10px' }}>
                            II. Ломаная и её типы
                        </Text>
                        <TheoryDTPABlock definition id='ломаная-и-типы'>
                            Ломаная — это геометрическая фигура, состоящая из отрезков, соединённых последовательно так, что конец одного отрезка является началом следующего.
                        </TheoryDTPABlock>
                        <TheoryDTPABlock theorem>
                            Ломаная называется замкнутой, если её начало совпадает с концом.
                        </TheoryDTPABlock>
                        <Paragraph ellipsis={{ defaultExpanded: true }} className='theory-paragraph'>
                            Замкнутая ломаная, у которой отрезки не пересекаются, называется многоугольником. Примером может служить треугольник или квадрат.
                        </Paragraph>
                        <TheoryDTPABlock proof>
                            Доказательство: Если ломаная замкнута, то последняя точка последнего отрезка совпадает с первой точкой первого отрезка. Если отрезки не пересекаются, кроме как в вершинах, то такая фигура образует многоугольник.
                        </TheoryDTPABlock>
                        <TheoryDTPABlock axiom>
                            Длина ломаной равна сумме длин её отрезков.
                        </TheoryDTPABlock>
                        <TheoryDTPABlock definition>
                            Ломаная называется простой, если её отрезки не пересекаются, кроме как в вершинах.
                        </TheoryDTPABlock>
                        <Paragraph ellipsis={{ defaultExpanded: true }} className='theory-paragraph'>
                            Простая ломаная может быть незамкнутой, например, ломаная ABC, где точки A, B и C соединены отрезками AB и BC, и они не пересекаются в других точках.
                        </Paragraph>
                        <Paragraph ellipsis={{ defaultExpanded: true }} className='theory-paragraph'>
                            Ломаные используются для моделирования сложных фигур, таких как траектории или границы объектов. Они играют важную роль в вычислительной геометрии.
                        </Paragraph>
                    </div>
                </div>
            </div>
            <ChatButton />
        </div>
    );
}

export default Theme1;
