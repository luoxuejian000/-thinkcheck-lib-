@Entry
@Component
struct SettingsPage {
  build() {
    Column() {
      Text('权重配置').fontSize(24).margin(20)
      Text('调整λU/λD/λA权重值（当前为经验预设，后续将通过实验校准）').fontSize(14).fontColor('#888888').padding(20)
      Text('法律(0.6,0.2,0.2) | 医疗(0.5,0.3,0.2) | 金融(0.3,0.4,0.3) | 通用(0.4,0.3,0.3)').fontSize(12).fontColor('#AAAAAA').padding(16)
      Text('⚙️ 可协商原则：以上权重均为协商起点，用户可根据场景需求调整。').fontSize(11).fontColor('#888888').padding(10)
      Text('鸿蒙端侧推理状态：' + (globalThis.hiAIReady ? 'HiAI可用' : 'CPU模式')).fontSize(12).margin({ top: 10 })
    }
  }
}