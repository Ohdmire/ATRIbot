# ATRIbot
一个主打osu查查查的bot

# 开发

目前已经进行重构，~~welcome to the new era.~~

## 基础建设

ATRIlib里面的文件夹功能比较独立 处理逻辑一般在外面的文件单独

ATRIproxy负责格式化函数返回的内容

### 需要考虑的问题

- 多模式储存用户信息
- 请求响应过于阻塞
- 帮助菜单

### 已解决
- ~~把表分开来 尽量独立储存 需要再联表查询~~
- ~~需要一个输入中转站 把输入的qq或者是osuname通通转换为user_id~~

## MongoDB储存的数据

- user表
储存基本信息和~~bp1-100的各项信息(array)~~ 现已分为bp表

- bp表
储存格式为列表

- score表
储存用户在谱面上的记录 精简score，去除无用数据

- bind表
储存用户的qqid

-group表
储存群的成员列表

# 特别鸣谢

## 技术支持

https://github.com/huhuibin147/interbotAPI


## 大土豪

[Pouxba](https://osu.ppy.sh/users/16378561) 138元

