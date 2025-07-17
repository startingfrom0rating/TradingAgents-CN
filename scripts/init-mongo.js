// MongoDB初始化脚本
// 创建数据库和集合，设置索引

// 切换到tradingagents数据库
db = db.getSiblingDB('tradingagents');

// 创建用户
db.createUser({
  user: 'tradingagents',
  pwd: 'tradingagents123',
  roles: [
    {
      role: 'readWrite',
      db: 'tradingagents'
    }
  ]
});

// 创建集合和索引
print('Creating collections and indexes...');

// 股票信息集合
db.stocks.createIndex({ "code": 1, "market": 1 }, { unique: true });
db.stocks.createIndex({ "market": 1 });
db.stocks.createIndex({ "industry": 1 });

// 历史数据集合
db.historical_data.createIndex({ "stock_code": 1, "date": -1 });
db.historical_data.createIndex({ "stock_code": 1, "date": 1 });
db.historical_data.createIndex({ "date": -1 });

// 基本面数据集合
db.fundamental_data.createIndex({ "stock_code": 1, "updated_at": -1 });
db.fundamental_data.createIndex({ "stock_code": 1 }, { unique: true });

// 公司信息集合
db.company_info.createIndex({ "stock_code": 1 }, { unique: true });

// 实时数据集合
db.realtime_data.createIndex({ "stock_code": 1, "timestamp": -1 });
db.realtime_data.createIndex({ "timestamp": -1 });

// 优先级配置集合
db.priority_configs.createIndex({ "market": 1, "data_type": 1 }, { unique: true });

// A/B测试配置集合
db.ab_test_configs.createIndex({ "test_name": 1 }, { unique: true });
db.ab_test_configs.createIndex({ "market": 1, "data_type": 1 });

// 更新日志集合
db.update_logs.createIndex({ "update_type": 1, "timestamp": -1 });
db.update_logs.createIndex({ "stock_code": 1, "timestamp": -1 });
db.update_logs.createIndex({ "timestamp": -1 });

// 数据质量集合
db.data_quality.createIndex({ "stock_code": 1, "data_type": 1, "timestamp": -1 });

// 插入一些示例数据
print('Inserting sample data...');

// 示例股票信息
db.stocks.insertMany([
  {
    code: "600036",
    name: "招商银行",
    market: "cn",
    industry: "银行",
    sector: "金融",
    status: "active",
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    code: "000001",
    name: "平安银行", 
    market: "cn",
    industry: "银行",
    sector: "金融",
    status: "active",
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    code: "000002",
    name: "万科A",
    market: "cn", 
    industry: "房地产",
    sector: "房地产",
    status: "active",
    created_at: new Date(),
    updated_at: new Date()
  }
]);

// 示例优先级配置
db.priority_configs.insertMany([
  {
    market: "cn",
    data_type: "historical",
    sources: [
      {
        source_name: "akshare",
        priority: 1,
        enabled: true,
        weight: 1.0,
        timeout_seconds: 30,
        max_requests_per_minute: 100,
        retry_count: 3
      },
      {
        source_name: "tushare",
        priority: 2,
        enabled: true,
        weight: 0.9,
        timeout_seconds: 30,
        max_requests_per_minute: 50,
        retry_count: 3
      },
      {
        source_name: "baostock",
        priority: 3,
        enabled: true,
        weight: 0.8,
        timeout_seconds: 30,
        max_requests_per_minute: 200,
        retry_count: 2
      }
    ],
    created_by: "system",
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    market: "cn",
    data_type: "fundamental",
    sources: [
      {
        source_name: "tushare",
        priority: 1,
        enabled: true,
        weight: 1.0,
        timeout_seconds: 30,
        max_requests_per_minute: 50,
        retry_count: 3
      },
      {
        source_name: "akshare",
        priority: 2,
        enabled: true,
        weight: 0.8,
        timeout_seconds: 30,
        max_requests_per_minute: 100,
        retry_count: 2
      }
    ],
    created_by: "system",
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    market: "cn",
    data_type: "realtime",
    sources: [
      {
        source_name: "akshare",
        priority: 1,
        enabled: true,
        weight: 1.0,
        timeout_seconds: 15,
        max_requests_per_minute: 200,
        retry_count: 2
      },
      {
        source_name: "tushare",
        priority: 2,
        enabled: true,
        weight: 0.7,
        timeout_seconds: 15,
        max_requests_per_minute: 100,
        retry_count: 2
      }
    ],
    created_by: "system",
    created_at: new Date(),
    updated_at: new Date()
  }
]);

print('MongoDB initialization completed successfully!');
