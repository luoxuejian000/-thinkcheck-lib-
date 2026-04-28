@Entry
@Component
struct DiagnosisPage {
  build() {
    Column() {
      Text('诊断详情').fontSize(24).margin(20)
      Text('展示单次诊断的U/D/A/H变化和概念漂移详情（支持分布式流转至平板查看）').fontSize(14).fontColor('#888888').padding(20)
    }
  }
}