// ChatBotApp.js
import React, { Fragment, useEffect, useState } from 'react';
import { Input, List, Avatar, Row, Col, Table, Spin } from 'antd';
import { useDispatch, useSelector } from 'react-redux';
import { addMessage, sendMessage } from './actions';
import { UserOutlined, DesktopOutlined } from '@ant-design/icons';

const { Search } = Input;

const UserServerAvatar = ({ type }) => {
  const getIcon = () => {
    switch (type) {
      case 'user':
        return <UserOutlined />;
      case 'server':
        return <DesktopOutlined />;
      default:
        return null;
    }
  };

  return (
    <Avatar
      style={{ backgroundColor: '#1890ff', marginRight: '8px' }}
      icon={getIcon()}
    />
  );
};

const TableView = ({ rows }) => {



  return <Table
    size='small'
    dataSource={rows}
    columns={rows.length > 0 ? Object.keys(rows[0]).map((col) => ({
      title: col.toUpperCase(),
      dataIndex: col,
      key: col,
    })) : []}
    scroll={{ x: true }}
    pagination={{
      defaultPageSize: 10,
      hideOnSinglePage: true,
    }}
    showSorterTooltip={{ show: true, placement: 'top' }}
    rowKey={(record, index) => index}
  />
  };


const MessageView = ({item}) => {
  const {data, errors , gen} = item.message
  return (
    <Fragment>
     <TableView rows = {data} />
     <TableView rows = {errors} />
     <TableView rows = {gen} />
    </Fragment>
  )
}

const CustomListItem = (item, index, totalLen) => {
  console.log(item)
  return(
    <List.Item style={{ marginBottom: index === totalLen - 1 ? '10vh' : '0vh' }}>
    <List.Item.Meta
      avatar={<UserServerAvatar type={item.type} />}
      title={item.type === 'user' ? 'You' : 'Bot'}
      description={
        item.type === 'user' ? (
          <div>{item.message}</div>
        ) : (
          <MessageView item={item}/ >
        )
      }
    />
  </List.Item>)
}
const ChatBotApp = () => {
  const [query, setQuery] = useState('');
  const dispatch = useDispatch();
  const messages = useSelector((state) => state.messages);

  const handleSearch = () => {
    dispatch(sendMessage(query));
    setQuery('');
  };
  return (
    <Row style={{ height: '90vh', flexDirection: 'row' }}>
      {/* List container with a scroll view */}
      <Col flex="1" style={{ overflowY: 'auto', padding: '20px', marginBottom: '10vh' }}>
      <List
        itemLayout="horizontal"
        dataSource={messages}
        renderItem={(item, index) => CustomListItem(item, index, messages.length)}
        />
      </Col>

      {/* User Input at the Bottom */}
      <Col span={24} style={{ position: 'fixed', bottom: 0, width: '100%', textAlign: 'center', padding: '20px' }}>
          <Search
            style={{ width: '100%', marginTop: '20px' }}
            placeholder="Type your query..."
            enterButton="Send"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onSearch={handleSearch}
          />
        </Col>
      </Row>
  );
};

export default ChatBotApp;
