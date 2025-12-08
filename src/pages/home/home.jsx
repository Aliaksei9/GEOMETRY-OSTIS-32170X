import { cloneElement } from 'react';
import Logo from '../../media/og.png';
import BackgroundImage from '../../media/1.jpeg';
import './home.css';
import { Avatar, Button, Dropdown, Typography, Divider } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router';
import ChatButton from '../../components/corner-chat/corner-chat-button';
import '../../index.css';
const { Text, Paragraph } = Typography;

function Home() {
    const navigate = useNavigate();

    // ──────────────────────────────── ПРОФИЛЬ ДРОПДАУН ────────────────────────────────
    const profileDropdownItems = [
        {
            key: 'header',
            label: (
                <div className="profile-header">
                    <Avatar
                        icon={<UserOutlined />}
                        size={88}
                        style={{ backgroundColor: '#6F60C1', color: 'white' }}
                    />
                    <div className="user-name">Alica Bubnova</div>
                </div>
            ),
            disabled: true,
        },
        { type: 'divider' },
        { key: 'profile', label: 'Профиль', onClick: () => navigate('/profile') },
        { key: 'balance', label: 'Баланс остиков' },
        { key: 'settings', label: 'Настройки', onClick: () => navigate('/settings') },
        { key: 'help', label: 'Помощь', onClick: () => navigate('/help') },
        { type: 'divider' },
        {
            key: 'logout',
            label: <span className="profile-logout">Выйти</span>,
            onClick: () => navigate('/'),
        },
    ];

    // ──────────────────────────────── ДРОПДАУНЫ ДЛЯ ТЕОРИИ/ТЕСТОВ/ЗАДАЧ (ТОЛЬКО ЭТО ИЗМЕНИЛ) ────────────────────────────────
    const theoryDropdownItems = [
        {
            key: '7',
            label: <Text strong style={{ fontSize: '18px', color: '#7B92DB' }}>7 класс</Text>,
            onClick: () => {
                navigate('/seven-grade-tests-theory-problems');
                setTimeout(() => {
                    const btn = document.querySelector('[data-tab="theory"]');
                    btn?.click();
                }, 100);
            },
        },
        { key: '8', label: <Text strong style={{ fontSize: '18px', color: '#7B92DB' }}>8 класс</Text>, disabled: true },
        { key: '9', label: <Text strong style={{ fontSize: '18px', color: '#7B92DB' }}>9 класс</Text>, disabled: true },
        { key: '10', label: <Text strong style={{ fontSize: '18px', color: '#7B92DB' }}>10 класс</Text>, disabled: true },
        { key: '11', label: <Text strong style={{ fontSize: '18px', color: '#7B92DB' }}>11 класс</Text>, disabled: true },
    ];

    const testsDropdownItems = [
        {
            key: '7',
            label: <Text strong style={{ fontSize: '18px', color: '#7B92DB' }}>7 класс</Text>,
            onClick: () => {
                navigate('/seven-grade-tests-theory-problems');
                setTimeout(() => {
                    const btn = document.querySelector('[data-tab="tests"]');
                    btn?.click();
                }, 100);
            },
        },
        { key: '8', label: <Text strong style={{ fontSize: '18px', color: '#7B92DB' }}>8 класс</Text>, disabled: true },
        { key: '9', label: <Text strong style={{ fontSize: '18px', color: '#7B92DB' }}>9 класс</Text>, disabled: true },
        { key: '10', label: <Text strong style={{ fontSize: '18px', color: '#7B92DB' }}>10 класс</Text>, disabled: true },
        { key: '11', label: <Text strong style={{ fontSize: '18px', color: '#7B92DB' }}>11 класс</Text>, disabled: true },
    ];

    const problemsDropdownItems = [
        {
            key: '7',
            label: <Text strong style={{ fontSize: '18px', color: '#7B92DB' }}>7 класс</Text>,
            onClick: () => {
                navigate('/seven-grade-tests-theory-problems');
                setTimeout(() => {
                    const btn = document.querySelector('[data-tab="problems"]');
                    btn?.click();
                }, 100);
            },
        },
        { key: '8', label: <Text strong style={{ fontSize: '18px', color: '#7B92DB' }}>8 класс</Text>, disabled: true },
        { key: '9', label: <Text strong style={{ fontSize: '18px', color: '#7B92DB' }}>9 класс</Text>, disabled: true },
        { key: '10', label: <Text strong style={{ fontSize: '18px', color: '#7B92DB' }}>10 класс</Text>, disabled: true },
        { key: '11', label: <Text strong style={{ fontSize: '18px', color: '#7B92DB' }}>11 класс</Text>, disabled: true },
    ];
    // ─────────────────────────────────────────────────────────────────────

    return (
        <div
            style={{
                width: '100%',
                height: '100%',
                overflowY: 'hidden',
                overflowX: 'hidden',
                backgroundImage: `url(${BackgroundImage})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                backgroundRepeat: 'no-repeat',
            }}
        >
            {/* ====================== ХЕДЕР ====================== */}
            <div id='home-header'>
                <div className='header-half' style={{ marginLeft: '-22.5px' }}>
                    <img src={Logo} className='header-logo' alt='OSTIS-geometry logo' />
                    <Dropdown
                        menu={{ items: theoryDropdownItems }}
                        placement='bottom'
                        dropdownRender={(menu) => (
                            <div style={{ width: '100%' }}>
                                {cloneElement(menu, { className: 'home-dropdown-menu' })}
                            </div>
                        )}
                    >
                        <Button className='button header-button'>
                            <span className='header-button-text'>Теория</span>
                        </Button>
                    </Dropdown>
                    <Dropdown
                        menu={{ items: testsDropdownItems }}
                        placement='bottom'
                        dropdownRender={(menu) => (
                            <div style={{ width: '100%' }}>
                                {cloneElement(menu, { className: 'home-dropdown-menu' })}
                            </div>
                        )}
                    >
                        <Button className='button header-button'>
                            <span className='header-button-text'>Тесты</span>
                        </Button>
                    </Dropdown>
                    <Dropdown
                        menu={{ items: problemsDropdownItems }}
                        placement='bottom'
                        dropdownRender={(menu) => (
                            <div style={{ width: '100%' }}>
                                {cloneElement(menu, { className: 'home-dropdown-menu' })}
                            </div>
                        )}
                    >
                        <Button className='button header-button'>
                            <span className='header-button-text'>Задачи</span>
                        </Button>
                    </Dropdown>
                    <Button className='button header-button'>
                        <span className='header-button-text'>Холст</span>
                    </Button>
                </div>
                {/* ====================== АВАТАРКА + НОВЫЙ КРАСИВЫЙ ПРОФИЛЬ-ДРОПДАУН ====================== */}
                <div className='header-half' style={{ flexDirection: 'row-reverse', marginRight: '20px' }}>
                    <Dropdown
                        menu={{ items: profileDropdownItems }}
                        placement="bottomRight"
                        trigger={['click']}
                        overlayClassName="home-profile-dropdown"
                        dropdownRender={(menu) => (
                            <div style={{ marginTop: '20px', borderRadius: '20px', overflow: 'hidden', boxShadow: '0 16px 40px rgba(111,96,193,0.28)' }}>
                                {cloneElement(menu)}
                            </div>
                        )}
                    >
                        <Avatar
                            icon={<UserOutlined />}
                            size={68}
                            style={{
                                cursor: 'pointer',
                                backgroundColor: 'white',
                                border: '3px solid #6F60C1',
                                color: '#6F60C1',
                                boxShadow: '0 0 12px rgba(111,96,193,0.35)',
                                transition: 'all 0.3s ease',
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
                            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                        />
                    </Dropdown>
                </div>
            </div>
            {/* ====================== ГЛАВНЫЙ КОНТЕНТ ====================== */}
	    <div id='home-main'>
                <div
                    style={{
                        width: '100%',
                        height: '100%',
                        backgroundColor: 'rgba(0, 0, 0, 0)',
                        display: 'flex',
                        alignItems: 'flex-start',
                        justifyContent: 'flex-start',
                        paddingTop: '15%',
                        paddingLeft: '1%',
                        color: 'white',
                    }}
                >
                    <div style={{ 
                        maxWidth: '80%', 
                        display: 'flex', 
                        flexDirection: 'column' 
                    }}>
                        <Text 
                            strong 
                            style={{ 
                                fontSize: '80px',
                                background: 'linear-gradient(90deg, #6F60C1 0%, #043BE4 100%)',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                backgroundClip: 'text',
                                textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
                                marginBottom: '10px'
                            }}
                        >
                            Добро пожаловать на OSTIS geometry
                        </Text>
                        <Text
                            strong
                            className='plain-text'
                            style={{ 
                                fontSize: '42px',
                                lineHeight: '45px',
                                whiteSpace: 'pre-line',
                                color: '#6F60C1',
                                textShadow: '1px 1px 2px rgba(0,0,0,0.8)'
                            }}
                        >
                            {`Интеллектуальная платформа\nдля обучения`}
                        </Text>
                        <Paragraph
                            strong
                            style={{ 
                                width: '140%',
                                marginTop: '250px',
                                fontSize: '40px',
                                lineHeight: '60px',
                                background: 'linear-gradient(90deg, #8C90E6 0%, #8C90E6 100%)',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                backgroundClip: 'text',
                                whiteSpace: 'pre-line'
                            }}
                        >
                            {`Интеллектуальная диалоговая\nсистема помогает пользователю в\nизучении отдельных тем по\n геометрии, в рамках учебной\nпрограммы РБ по геометрии`}
                        </Paragraph>
                    </div>
                </div>
            </div>
            <ChatButton />
        </div>
    );
}

export default Home;
