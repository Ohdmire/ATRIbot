# ATRIbot
一个主打osu查查查的bot

# 开发

## 基础建设

所有功能处理逻辑先对接`Core.py`
所有访问请求都要通过`ATRIproxy.py`格式化数据

### 急急急

- [x] MongoDB读写数据(需要制定规范标准)
- [x] osuapiv2
- [x] rosu查询谱面pp
  
### 不是很急的
- [ ] draw绘图
- [x] FASTAPI包装
- [x] Onebotv11对接

## MongoDB储存的数据

- user表
储存基本信息和bp1-100的scoreid

- beatmap表
储存用户在谱面上的记录

- bind表
储存用户的qqid

-group表
储存群的成员列表